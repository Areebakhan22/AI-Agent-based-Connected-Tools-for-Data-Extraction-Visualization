"""
Google Slides Generator Module

This module creates Google Slides presentations from structured SysML data.
Each part becomes a rectangle shape, and each connection becomes an arrow.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Dict, List
import json
import os

# Google Slides API scope - only need to modify presentations
SCOPES = ['https://www.googleapis.com/auth/presentations']

# Standard Google Slides dimensions (in points)
SLIDE_WIDTH = 720   # Standard slide width
SLIDE_HEIGHT = 540   # Standard slide height
MARGIN = 50         # Margin from edges


def authenticate_google_slides():
    """
    Authenticate and return Google Slides API service.
    
    This function handles OAuth2 authentication. On first run, it will
    open a browser for user consent. Credentials are saved for future use.
    
    Returns:
        Google Slides API service object
        
    Note:
        You need to:
        1. Create a project in Google Cloud Console
        2. Enable Google Slides API
        3. Create OAuth 2.0 credentials (Desktop app)
        4. Save credentials as 'credentials.json' in the project directory
    """
    creds = None
    
    # Check if we have saved credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, get user authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json not found. Please download OAuth 2.0 "
                    "credentials from Google Cloud Console and save as 'credentials.json'"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('slides', 'v1', credentials=creds)


def calculate_text_dimensions(text: str, font_size: float = 11, max_width: float = None) -> Dict:
    """
    Estimate text dimensions for proper shape sizing.
    
    Args:
        text: Text content
        font_size: Font size in points
        max_width: Maximum width for wrapping
        
    Returns:
        Dictionary with estimated width and height
    """
    # Rough estimation: ~6-7 pixels per character at 11pt font
    chars_per_line = int((max_width or 200) / (font_size * 0.6)) if max_width else len(text)
    num_lines = max(1, (len(text) + chars_per_line - 1) // chars_per_line)
    
    estimated_width = min(len(text) * (font_size * 0.6), max_width or 200)
    estimated_height = num_lines * (font_size * 1.5) + 10  # Line height + padding
    
    return {
        'width': max(estimated_width, 80),  # Minimum width
        'height': max(estimated_height, 40)  # Minimum height
    }


def check_overlap(rect1: Dict, rect2: Dict, padding: float = 15) -> bool:
    """
    Check if two rectangles overlap (with optional padding).
    
    Args:
        rect1: Dictionary with x, y, width, height
        rect2: Dictionary with x, y, width, height
        padding: Minimum spacing required between rectangles
        
    Returns:
        True if rectangles overlap (including padding)
    """
    return not (
        rect1['x'] + rect1['width'] + padding < rect2['x'] or
        rect2['x'] + rect2['width'] + padding < rect1['x'] or
        rect1['y'] + rect1['height'] + padding < rect2['y'] or
        rect2['y'] + rect2['height'] + padding < rect1['y']
    )


def get_rect_bounds(elem: Dict) -> Dict:
    """
    Get bounding rectangle for an element (handles different types).
    
    Args:
        elem: Element dict with type and position info
        
    Returns:
        Dictionary with x, y, width, height
    """
    if elem['type'] == 'actor':
        # Actor is a circle, convert to bounding box
        size = elem['size']
        return {
            'x': elem['x'] - size / 2,
            'y': elem['y'] - size / 2,
            'width': size,
            'height': size
        }
    else:
        return {
            'x': elem['x'],
            'y': elem['y'],
            'width': elem['width'],
            'height': elem['height']
        }


def calculate_professional_layout(data: Dict) -> Dict:
    """
    Calculate professional SysML-style layout with collision detection.
    
    Strategy:
    1. Calculate all element sizes first (based on text content)
    2. Define layout zones (use cases center, actors sides, parts bottom)
    3. Position elements with collision detection
    4. Ensure proper spacing and no overlaps
    
    Args:
        data: Dictionary with parts, actors, use_cases, connections, hierarchy
        
    Returns:
        Dictionary with layout information including system boundary
    """
    parts = data.get('parts', [])
    actors = data.get('actors', [])
    use_cases = data.get('use_cases', [])
    connections = data.get('connections', [])
    hierarchy = data.get('hierarchy', {})
    
    # Find system name
    system_name = None
    top_level_parts = [p for p in parts if p.get('is_top_level', False)]
    if top_level_parts:
        system_name = top_level_parts[0]['name']
    elif parts:
        system_name = parts[0]['name']
    else:
        system_name = "System"
    
    # System boundary - use 8% margin
    boundary_margin = SLIDE_WIDTH * 0.08
    boundary_x = boundary_margin
    boundary_y = boundary_margin + 40  # Extra for title
    boundary_width = SLIDE_WIDTH - 2 * boundary_margin
    boundary_height = SLIDE_HEIGHT - 2 * boundary_margin - 40
    
    layout = {
        'system_boundary': {
            'name': system_name,
            'x': boundary_x,
            'y': boundary_y,
            'width': boundary_width,
            'height': boundary_height
        },
        'elements': {}
    }
    
    # Content area inside boundary
    content_padding = 40
    content_x = boundary_x + content_padding
    content_y = boundary_y + 70  # Space for title
    content_width = boundary_width - 2 * content_padding
    content_height = boundary_height - 90  # Top and bottom padding
    
    # Build connection map
    connection_map = {}
    for conn in connections:
        from_elem = conn['from']
        to_elem = conn['to']
        if from_elem not in connection_map:
            connection_map[from_elem] = []
        connection_map[from_elem].append(to_elem)
        if to_elem not in connection_map:
            connection_map[to_elem] = []
        connection_map[to_elem].append(from_elem)
    
    # Step 1: Calculate sizes for all elements FIRST
    child_parts = [p for p in parts if not p.get('is_top_level', False)]
    
    # Calculate use case sizes
    use_case_sizes = {}
    min_uc_width = 160
    max_uc_width = min(220, content_width * 0.4)
    base_uc_spacing = 40
    
    for uc in use_cases:
        text_dims = calculate_text_dimensions(uc['name'], font_size=11, max_width=max_uc_width - 20)
        use_case_sizes[uc['name']] = {
            'width': max(min_uc_width, min(text_dims['width'] + 30, max_uc_width)),
            'height': max(65, text_dims['height'] + 20)
        }
    
    # Calculate part sizes
    part_sizes = {}
    num_parts = len(child_parts)
    if num_parts > 0:
        # Calculate available width for parts
        available_part_width = content_width * 0.85  # Leave 15% for margins
        min_part_width = 90
        max_part_width = min(120, available_part_width / num_parts - 20)
        part_spacing = 25
        
        for part in child_parts:
            text_dims = calculate_text_dimensions(part['name'], font_size=11, max_width=max_part_width - 15)
            part_sizes[part['name']] = {
                'width': max(min_part_width, min(text_dims['width'] + 20, max_part_width)),
                'height': max(50, text_dims['height'] + 15)
            }
    
    # Actor size (circles)
    actor_size = min(55, content_width * 0.075)
    actor_size = max(actor_size, 45)
    
    # Step 2: Position USE CASES in center (horizontally)
    num_use_cases = len(use_cases)
    existing_rects = []
    
    if num_use_cases > 0:
        # Calculate total width needed
        total_uc_width = sum(uc_sizes['width'] for uc_sizes in use_case_sizes.values())
        total_uc_width += (num_use_cases - 1) * base_uc_spacing
        
        # If too wide, reduce spacing
        if total_uc_width > content_width * 0.85:
            # Reduce spacing
            available_for_spacing = content_width * 0.85 - total_uc_width + (num_use_cases - 1) * base_uc_spacing
            uc_spacing = max(20, available_for_spacing / (num_use_cases - 1)) if num_use_cases > 1 else 0
        else:
            uc_spacing = base_uc_spacing
        
        # Center horizontally
        uc_start_x = content_x + (content_width - total_uc_width + (num_use_cases - 1) * uc_spacing) / 2
        # Position in middle area (40% from top of content)
        uc_y = content_y + content_height * 0.40
        
        for idx, uc in enumerate(use_cases):
            if idx == 0:
                x = uc_start_x
            else:
                prev_uc = use_cases[idx - 1]
                prev_width = use_case_sizes[prev_uc['name']]['width']
                x = layout['elements'][prev_uc['name']]['x'] + prev_width + uc_spacing
            
            uc_info = {
                'type': 'use_case',
                'x': x,
                'y': uc_y,
                'width': use_case_sizes[uc['name']]['width'],
                'height': use_case_sizes[uc['name']]['height']
            }
            layout['elements'][uc['name']] = uc_info
            existing_rects.append(get_rect_bounds(uc_info))
    else:
        uc_y = content_y + content_height * 0.40
    
    # Step 3: Position ACTORS on left and right sides
    # Group actors by side
    left_actors = []
    right_actors = []
    
    for actor in actors:
        actor_name = actor['name']
        # Find connected use case
        connected_uc = None
        if actor_name in connection_map:
            for connected in connection_map[actor_name]:
                if any(uc['name'] == connected for uc in use_cases):
                    connected_uc = connected
                    break
        
        if connected_uc and connected_uc in layout['elements']:
            uc_x = layout['elements'][connected_uc]['x']
            center_x = content_x + content_width / 2
            if uc_x < center_x:
                left_actors.append((actor_name, connected_uc))
            else:
                right_actors.append((actor_name, connected_uc))
        else:
            # Alternate
            if len(left_actors) <= len(right_actors):
                left_actors.append((actor_name, None))
            else:
                right_actors.append((actor_name, None))
    
    # Position left actors
    left_zone_x = content_x + 25
    left_zone_width = content_width * 0.15
    actor_spacing = 70
    
    for idx, (actor_name, uc_name) in enumerate(left_actors):
        if uc_name and uc_name in layout['elements']:
            # Align with use case
            uc_info = layout['elements'][uc_name]
            actor_y = uc_info['y'] + uc_info['height'] / 2
            # Offset vertically if multiple actors
            actor_y += (idx - len(left_actors) / 2) * actor_spacing
        else:
            # Distribute in top area
            top_area_start = content_y + 30
            top_area_height = uc_y - content_y - 30
            if len(left_actors) > 1:
                actor_y = top_area_start + (top_area_height / (len(left_actors) + 1)) * (idx + 1)
            else:
                actor_y = top_area_start + top_area_height / 2
        
        # Check for overlap and adjust
        actor_rect = {
            'x': left_zone_x,
            'y': actor_y - actor_size / 2,
            'width': actor_size,
            'height': actor_size
        }
        
        # Adjust if overlaps
        for existing in existing_rects:
            if check_overlap(actor_rect, existing):
                # Move down
                actor_rect['y'] = existing['y'] + existing['height'] + 20
        
        layout['elements'][actor_name] = {
            'type': 'actor',
            'x': actor_rect['x'] + actor_size / 2,
            'y': actor_rect['y'] + actor_size / 2,
            'size': actor_size
        }
        existing_rects.append(get_rect_bounds(layout['elements'][actor_name]))
    
    # Position right actors
    right_zone_x = content_x + content_width - content_width * 0.15 - 25
    
    for idx, (actor_name, uc_name) in enumerate(right_actors):
        if uc_name and uc_name in layout['elements']:
            # Align with use case
            uc_info = layout['elements'][uc_name]
            actor_y = uc_info['y'] + uc_info['height'] / 2
            actor_y += (idx - len(right_actors) / 2) * actor_spacing
        else:
            # Distribute in top area
            top_area_start = content_y + 30
            top_area_height = uc_y - content_y - 30
            if len(right_actors) > 1:
                actor_y = top_area_start + (top_area_height / (len(right_actors) + 1)) * (idx + 1)
            else:
                actor_y = top_area_start + top_area_height / 2
        
        # Check for overlap
        actor_rect = {
            'x': right_zone_x,
            'y': actor_y - actor_size / 2,
            'width': actor_size,
            'height': actor_size
        }
        
        for existing in existing_rects:
            if check_overlap(actor_rect, existing):
                actor_rect['y'] = existing['y'] + existing['height'] + 20
        
        layout['elements'][actor_name] = {
            'type': 'actor',
            'x': actor_rect['x'] + actor_size / 2,
            'y': actor_rect['y'] + actor_size / 2,
            'size': actor_size
        }
        existing_rects.append(get_rect_bounds(layout['elements'][actor_name]))
    
    # Step 4: Position PARTS at bottom
    if num_parts > 0:
        # Calculate total width needed
        total_part_width = sum(part_sizes[p['name']]['width'] for p in child_parts)
        total_part_width += (num_parts - 1) * part_spacing
        
        # If too wide, reduce spacing
        if total_part_width > content_width * 0.9:
            available_for_spacing = content_width * 0.9 - total_part_width + (num_parts - 1) * part_spacing
            part_spacing = max(15, available_for_spacing / (num_parts - 1)) if num_parts > 1 else 0
        
        # Center horizontally
        part_start_x = content_x + (content_width - total_part_width) / 2
        # Position in bottom area (85% from top of content)
        part_y = content_y + content_height * 0.85
        
        for idx, part in enumerate(child_parts):
            if idx == 0:
                x = part_start_x
            else:
                prev_part = child_parts[idx - 1]
                prev_width = part_sizes[prev_part['name']]['width']
                x = layout['elements'][prev_part['name']]['x'] + prev_width + part_spacing
            
            part_info = {
                'type': 'part',
                'x': x,
                'y': part_y,
                'width': part_sizes[part['name']]['width'],
                'height': part_sizes[part['name']]['height']
            }
            
            # Check for overlap
            part_rect = get_rect_bounds(part_info)
            for existing in existing_rects:
                if check_overlap(part_rect, existing):
                    # Move down
                    part_info['y'] = existing['y'] + existing['height'] + 20
                    part_rect = get_rect_bounds(part_info)
            
            layout['elements'][part['name']] = part_info
            existing_rects.append(get_rect_bounds(part_info))
    
    # Step 5: Handle other elements (SoI, etc.)
    all_element_names = {e['name'] for e in parts + actors + use_cases}
    for conn in connections:
        for elem_name in [conn['from'], conn['to']]:
            if elem_name not in layout['elements'] and elem_name not in all_element_names:
                # Default sizing
                default_width = 100
                default_height = 50
                
                if elem_name in ['SoI', 'Subject'] or 'SoI' in elem_name:
                    # Position below first use case
                    if use_cases and use_cases[0]['name'] in layout['elements']:
                        uc_info = layout['elements'][use_cases[0]['name']]
                        soi_y = uc_info['y'] + uc_info['height'] + 30
                        soi_x = uc_info['x'] + uc_info['width'] / 2 - default_width / 2
                    else:
                        soi_x = content_x + content_width / 2 - default_width / 2
                        soi_y = uc_y + 100
                    
                    soi_rect = {'x': soi_x, 'y': soi_y, 'width': default_width, 'height': default_height}
                    
                    # Check overlap
                    for existing in existing_rects:
                        if check_overlap(soi_rect, existing):
                            soi_rect['y'] = existing['y'] + existing['height'] + 20
                    
                    layout['elements'][elem_name] = {
                        'type': 'part',
                        'x': soi_rect['x'],
                        'y': soi_rect['y'],
                        'width': default_width,
                        'height': default_height
                    }
                    existing_rects.append(soi_rect)
                else:
                    # Default position at bottom center
                    default_x = content_x + content_width / 2 - default_width / 2
                    default_y = content_y + content_height * 0.90
                    
                    default_rect = {'x': default_x, 'y': default_y, 'width': default_width, 'height': default_height}
                    
                    for existing in existing_rects:
                        if check_overlap(default_rect, existing):
                            default_rect['y'] = existing['y'] + existing['height'] + 20
                    
                    layout['elements'][elem_name] = {
                        'type': 'part',
                        'x': default_rect['x'],
                        'y': default_rect['y'],
                        'width': default_width,
                        'height': default_height
                    }
                    existing_rects.append(default_rect)
    
    return layout


def create_presentation(service, title: str = "SysML Visualization"):
    """
    Create a new Google Slides presentation.
    
    Args:
        service: Google Slides API service object
        title: Title of the presentation
        
    Returns:
        Presentation ID
    """
    try:
        presentation = service.presentations().create(
            body={'title': title}
        ).execute()
        
        presentation_id = presentation.get('presentationId')
        print(f"Created presentation: {presentation_id}")
        print(f"View it at: https://docs.google.com/presentation/d/{presentation_id}")
        
        return presentation_id
    except HttpError as error:
        print(f"An error occurred: {error}")
        raise


def draw_system_boundary(service, presentation_id, page_id, 
                         system_name: str, x: float, y: float,
                         width: float, height: float) -> str:
    """
    Draw system boundary - large rectangle with title in top-left.
    """
    # Truncate to ensure object ID is <= 50 characters
    short_name = system_name[:30] if len(system_name) > 30 else system_name
    object_id = f'sys_{short_name}'[:50]
    
    requests = [{
        'createShape': {
            'objectId': object_id,
            'shapeType': 'RECTANGLE',
            'elementProperties': {
                'pageObjectId': page_id,
                'size': {
                    'height': {'magnitude': height, 'unit': 'PT'},
                    'width': {'magnitude': width, 'unit': 'PT'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'PT'
                }
            }
        }
    }, {
        'updateShapeProperties': {
            'objectId': object_id,
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {
                        'color': {
                            'rgbColor': {
                                'red': 0.9,
                                'green': 0.9,
                                'blue': 0.9
                            }
                        }
                    }
                },
                'outline': {
                    'outlineFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 0.2,
                                    'green': 0.2,
                                    'blue': 0.2
                                }
                            }
                        }
                    },
                    'weight': {'magnitude': 2, 'unit': 'PT'}
                }
            },
            'fields': 'shapeBackgroundFill,outline'
        }
    }, {
        'insertText': {
            'objectId': object_id,
            'text': system_name,
            'insertionIndex': 0
        }
    }, {
        'updateParagraphStyle': {
            'objectId': object_id,
            'style': {
                'alignment': 'START',
                'spaceAbove': {'magnitude': 8, 'unit': 'PT'},
                'spaceBelow': {'magnitude': 0, 'unit': 'PT'},
                'direction': 'LEFT_TO_RIGHT'
            },
            'fields': 'alignment,spaceAbove,spaceBelow,direction'
        }
    }, {
        'updateTextStyle': {
            'objectId': object_id,
            'style': {
                'bold': True,
                'fontSize': {'magnitude': 14, 'unit': 'PT'}
            },
            'fields': 'bold,fontSize'
        }
    }]
    
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    return object_id


def draw_part(service, presentation_id, page_id,
              part_name: str, x: float, y: float,
              width: float, height: float) -> str:
    """
    Draw a part as a rectangle.
    """
    # Truncate to ensure object ID is <= 50 characters
    short_name = part_name[:40] if len(part_name) > 40 else part_name
    object_id = f'part_{short_name}'[:50]
    
    requests = [{
        'createShape': {
            'objectId': object_id,
            'shapeType': 'RECTANGLE',
            'elementProperties': {
                'pageObjectId': page_id,
                'size': {
                    'height': {'magnitude': height, 'unit': 'PT'},
                    'width': {'magnitude': width, 'unit': 'PT'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'PT'
                }
            }
        }
    }, {
        'updateShapeProperties': {
            'objectId': object_id,
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {
                        'color': {
                            'rgbColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        }
                    }
                },
                'outline': {
                    'outlineFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 0.0,
                                    'green': 0.0,
                                    'blue': 0.0
                                }
                            }
                        }
                    },
                    'weight': {'magnitude': 1.5, 'unit': 'PT'}
                }
            },
            'fields': 'shapeBackgroundFill,outline'
        }
        }, {
            'insertText': {
            'objectId': object_id,
                'text': part_name,
                'insertionIndex': 0
            }
        }, {
            'updateParagraphStyle': {
            'objectId': object_id,
                'style': {
                    'alignment': 'CENTER',
                    'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                'spaceBelow': {'magnitude': 0, 'unit': 'PT'}
                },
            'fields': 'alignment,spaceAbove,spaceBelow'
            }
        }, {
            'updateTextStyle': {
            'objectId': object_id,
                'style': {
                    'bold': False,
                    'fontSize': {'magnitude': 11, 'unit': 'PT'}
                },
                'fields': 'bold,fontSize'
            }
        }]
        
    service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
    return object_id


def draw_use_case(service, presentation_id, page_id,
                  use_case_name: str, x: float, y: float,
                  width: float, height: float) -> str:
    """
    Draw a use case as a rounded rectangle.
    """
    # Truncate to ensure object ID is <= 50 characters
    short_name = use_case_name[:35] if len(use_case_name) > 35 else use_case_name
    object_id = f'uc_{short_name}'[:50]
    
    requests = [{
        'createShape': {
            'objectId': object_id,
            'shapeType': 'ROUND_RECTANGLE',
            'elementProperties': {
                'pageObjectId': page_id,
                'size': {
                    'height': {'magnitude': height, 'unit': 'PT'},
                    'width': {'magnitude': width, 'unit': 'PT'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'PT'
                }
            }
        }
    }, {
        'updateShapeProperties': {
            'objectId': object_id,
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {
                        'color': {
                            'rgbColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        }
                    }
                },
                'outline': {
                    'outlineFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 0.0,
                                    'green': 0.0,
                                    'blue': 0.0
                                }
                            }
                        }
                    },
                    'weight': {'magnitude': 1.5, 'unit': 'PT'}
                }
            },
            'fields': 'shapeBackgroundFill,outline'
        }
    }, {
        'insertText': {
            'objectId': object_id,
            'text': use_case_name,
            'insertionIndex': 0
        }
    }, {
        'updateParagraphStyle': {
            'objectId': object_id,
            'style': {
                'alignment': 'CENTER',
                'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                'spaceBelow': {'magnitude': 0, 'unit': 'PT'}
            },
            'fields': 'alignment,spaceAbove,spaceBelow'
        }
    }, {
        'updateTextStyle': {
            'objectId': object_id,
            'style': {
                'bold': False,
                'fontSize': {'magnitude': 11, 'unit': 'PT'}
            },
            'fields': 'bold,fontSize'
        }
    }]
    
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    return object_id


def draw_actor(service, presentation_id, page_id,
               actor_name: str, x: float, y: float,
               size: float = 50) -> str:
    """
    Draw an actor as a circle.
    """
    # Truncate to ensure object ID is <= 50 characters
    short_name = actor_name[:40] if len(actor_name) > 40 else actor_name
    object_id = f'act_{short_name}'[:50]
    
    # Calculate position for top-left corner
    circle_x = x - size / 2
    circle_y = y - size / 2
    
    requests = [{
        'createShape': {
            'objectId': object_id,
            'shapeType': 'ELLIPSE',
            'elementProperties': {
                'pageObjectId': page_id,
                'size': {
                    'height': {'magnitude': size, 'unit': 'PT'},
                    'width': {'magnitude': size, 'unit': 'PT'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': circle_x,
                    'translateY': circle_y,
                    'unit': 'PT'
                }
            }
        }
    }, {
        'updateShapeProperties': {
            'objectId': object_id,
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {
                        'color': {
                            'rgbColor': {
                                'red': 1.0,
                                'green': 1.0,
                                'blue': 1.0
                            }
                        }
                    }
                },
                'outline': {
                    'outlineFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 0.0,
                                    'green': 0.0,
                                    'blue': 0.0
                                }
                            }
                        }
                    },
                    'weight': {'magnitude': 1.5, 'unit': 'PT'}
                }
            },
            'fields': 'shapeBackgroundFill,outline'
        }
    }, {
        'insertText': {
            'objectId': object_id,
            'text': actor_name,
            'insertionIndex': 0
        }
    }, {
        'updateParagraphStyle': {
            'objectId': object_id,
            'style': {
                'alignment': 'CENTER',
                'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                'spaceBelow': {'magnitude': 0, 'unit': 'PT'}
            },
            'fields': 'alignment,spaceAbove,spaceBelow'
        }
    }, {
        'updateTextStyle': {
            'objectId': object_id,
            'style': {
                'bold': False,
                'fontSize': {'magnitude': 10, 'unit': 'PT'}
            },
            'fields': 'bold,fontSize'
        }
    }]
    
    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()
    
    return object_id


def draw_connection(service, presentation_id, page_id,
                   from_shape_id: str, to_shape_id: str,
                   from_layout: Dict, to_layout: Dict,
                   has_arrow: bool = True):
    """
    Draw a connection between two shapes using thin rectangles (compatible approach).
    """
    # Calculate connection points (edges of shapes)
    from_center_x = from_layout['x'] + from_layout['width'] / 2
    from_center_y = from_layout['y'] + from_layout['height'] / 2
    to_center_x = to_layout['x'] + to_layout['width'] / 2
    to_center_y = to_layout['y'] + to_layout['height'] / 2
    
    # Find closest edges
    dx = to_center_x - from_center_x
    dy = to_center_y - from_center_y
    
    # Calculate start point on edge of source shape
    if abs(dx) > abs(dy):
        # Horizontal connection
        if dx > 0:
            start_x = from_layout['x'] + from_layout['width']
            start_y = from_center_y
        else:
            start_x = from_layout['x']
            start_y = from_center_y
    else:
        # Vertical connection
        if dy > 0:
            start_x = from_center_x
            start_y = from_layout['y'] + from_layout['height']
        else:
            start_x = from_center_x
            start_y = from_layout['y']
    
    # Calculate end point on edge of target shape
    if abs(dx) > abs(dy):
        if dx > 0:
            end_x = to_layout['x']
            end_y = to_center_y
        else:
            end_x = to_layout['x'] + to_layout['width']
            end_y = to_center_y
    else:
        if dy > 0:
            end_x = to_center_x
            end_y = to_layout['y']
        else:
            end_x = to_center_x
            end_y = to_layout['y'] + to_layout['height']
    
    # Calculate line dimensions
    line_width = abs(end_x - start_x)
    line_height = abs(end_y - start_y)
    line_x = min(start_x, end_x)
    line_y = min(start_y, end_y)
    
    # Create connector ID
    from_short = from_shape_id.replace('part_', '').replace('uc_', '').replace('act_', '').replace('sys_', '')[:15]
    to_short = to_shape_id.replace('part_', '').replace('uc_', '').replace('act_', '').replace('sys_', '')[:15]
    connector_id = f'conn_{from_short}_{to_short}'[:50]
    
    # Use thin rectangle approach
    is_horizontal = line_width > line_height
    
    if is_horizontal:
        line_thickness = 2
        conn_width = max(line_width, 1)
        conn_height = line_thickness
    else:
        line_thickness = 2
        conn_width = line_thickness
        conn_height = max(line_height, 1)
        
        requests = [{
            'createShape': {
                'objectId': connector_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': conn_height, 'unit': 'PT'},
                        'width': {'magnitude': conn_width, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': line_x,
                        'translateY': line_y,
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': connector_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 0.0,
                                    'green': 0.0,
                                    'blue': 0.0
                                }
                            }
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': {
                                        'red': 0.0,
                                        'green': 0.0,
                                        'blue': 0.0
                                    }
                                }
                            }
                        },
                        'weight': {'magnitude': 1, 'unit': 'PT'}
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }]
        
    # Add arrowhead if requested
    if has_arrow:
        arrow_size = 8
        arrow_id = f'{connector_id}_arr'[:50]
        
        if is_horizontal:
            if dx > 0:
                arrow_x = end_x - arrow_size
                arrow_y = end_y - arrow_size / 2
            else:
                arrow_x = end_x
                arrow_y = end_y - arrow_size / 2
        else:
            if dy > 0:
                arrow_x = end_x - arrow_size / 2
                arrow_y = end_y - arrow_size
            else:
                arrow_x = end_x - arrow_size / 2
                arrow_y = end_y
        
        requests.append({
            'createShape': {
                'objectId': arrow_id,
                'shapeType': 'TRIANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': arrow_size, 'unit': 'PT'},
                        'width': {'magnitude': arrow_size, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': arrow_x,
                        'translateY': arrow_y,
                        'unit': 'PT'
                    }
                }
            }
        })
        requests.append({
            'updateShapeProperties': {
                'objectId': arrow_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 0.0,
                                    'green': 0.0,
                                    'blue': 0.0
                                }
                            }
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': {
                                        'red': 0.0,
                                        'green': 0.0,
                                        'blue': 0.0
                                    }
                                }
                            }
                        },
                        'weight': {'magnitude': 1, 'unit': 'PT'}
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        })
    
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()


def generate_slides(data: Dict, presentation_title: str = "SysML Visualization"):
    """
    Main function to generate Google Slides from parsed SysML data.
    """
    # Authenticate and get service
    service = authenticate_google_slides()
    
    # Create new presentation
    presentation_id = create_presentation(service, presentation_title)
    
    # Get the first slide page ID
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    page_id = presentation.get('slides')[0]['objectId']
    
    # Set slide background to white and remove placeholders
    try:
        page_elements = presentation.get('slides')[0].get('pageElements', [])
        delete_requests = []
        
        for element in page_elements:
            shape = element.get('shape', {})
            placeholder = shape.get('placeholder', {})
            if placeholder:
                placeholder_type = placeholder.get('type')
                if placeholder_type in ['TITLE', 'SUBTITLE', 'CENTERED_TITLE']:
                    delete_requests.append({
                        'deleteObject': {
                            'objectId': element.get('objectId')
                        }
                    })
        
        requests = [{
            'updatePageProperties': {
                'objectId': page_id,
                'pageProperties': {
                    'pageBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': {
                                    'red': 1.0,
                                    'green': 1.0,
                                    'blue': 1.0
                                }
                            }
                        }
                    }
                },
                'fields': 'pageBackgroundFill'
            }
        }]
        
        requests.extend(delete_requests)
        
        if requests:
            service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
            if delete_requests:
                print("✓ Slide background set to white and placeholders removed")
    except Exception as e:
        print(f"Warning: Could not set background: {e}")
    
    # Use professional SysML-style layout
    layout = calculate_professional_layout(data)
    
    # Draw system boundary first
    boundary = layout['system_boundary']
    draw_system_boundary(
        service, presentation_id, page_id,
        boundary['name'],
        boundary['x'], boundary['y'],
        boundary['width'], boundary['height']
    )
    
    # Draw all elements with appropriate shapes
    shape_ids = {}
    element_layouts = {}
    
    for element_name, element_info in layout['elements'].items():
        elem_type = element_info['type']
        
        if elem_type == 'part':
            shape_id = draw_part(
            service, presentation_id, page_id,
                element_name,
                element_info['x'], element_info['y'],
                element_info['width'], element_info['height']
            )
            element_layouts[element_name] = {
                'x': element_info['x'],
                'y': element_info['y'],
                'width': element_info['width'],
                'height': element_info['height']
            }
        elif elem_type == 'use_case':
            shape_id = draw_use_case(
                service, presentation_id, page_id,
                element_name,
                element_info['x'], element_info['y'],
                element_info['width'], element_info['height']
            )
            element_layouts[element_name] = {
                'x': element_info['x'],
                'y': element_info['y'],
                'width': element_info['width'],
                'height': element_info['height']
            }
        elif elem_type == 'actor':
            shape_id = draw_actor(
                service, presentation_id, page_id,
                element_name,
                element_info['x'], element_info['y'],
                element_info['size']
            )
            # For actors, layout uses center point, convert to bounding box
            actor_size = element_info['size']
            element_layouts[element_name] = {
                'x': element_info['x'] - actor_size / 2,
                'y': element_info['y'] - actor_size / 2,
                'width': actor_size,
                'height': actor_size
            }
        else:
            # Default to part
            shape_id = draw_part(
                service, presentation_id, page_id,
                element_name,
                element_info['x'], element_info['y'],
                element_info.get('width', 120), element_info.get('height', 50)
            )
            element_layouts[element_name] = {
                'x': element_info['x'],
                'y': element_info['y'],
                'width': element_info.get('width', 120),
                'height': element_info.get('height', 50)
            }
        
        shape_ids[element_name] = shape_id
    
    # Draw connections AFTER all shapes are positioned
    for conn in data.get('connections', []):
        from_elem = conn['from']
        to_elem = conn['to']
        
        if from_elem in shape_ids and to_elem in shape_ids:
            if from_elem in element_layouts and to_elem in element_layouts:
                has_arrow = True
                draw_connection(
                service, presentation_id, page_id,
                    shape_ids[from_elem], shape_ids[to_elem],
                    element_layouts[from_elem], element_layouts[to_elem],
                    has_arrow=has_arrow
            )
    
    url = f"https://docs.google.com/presentation/d/{presentation_id}"
    return presentation_id, url

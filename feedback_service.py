#!/usr/bin/env python3
"""
Bidirectional Feedback Service

Enables near-real-time bidirectional data exchange between:
- Tool A (visualize_sysml.py): JSON → Slides
- Tool B (this service): Slides → JSON feedback

This service monitors Google Slides for user edits and extracts feedback.
"""

import json
import time
import sys
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os

SCOPES = ['https://www.googleapis.com/auth/presentations.readonly']


class FeedbackService:
    """
    Service for extracting user feedback from Google Slides.
    """
    
    def __init__(self):
        self.service = None
        self.element_mapping = {}  # Maps shape IDs to element IDs
    
    def authenticate(self):
        """Authenticate and get Google Slides service."""
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download OAuth 2.0 "
                        "credentials from Google Cloud Console and save as 'credentials.json'"
                    )
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('slides', 'v1', credentials=creds)
        return self.service
    
    def load_element_mapping(self, mapping_file: str):
        """Load element mapping from JSON file."""
        with open(mapping_file, 'r') as f:
            self.element_mapping = json.load(f)
        print(f"✓ Loaded element mapping from: {mapping_file}")
    
    def extract_feedback(self, presentation_id: str, element_mapping: Optional[Dict] = None) -> Dict:
        """
        Extract user feedback from Google Slides.
        
        Args:
            presentation_id: Google Slides presentation ID
            element_mapping: Optional mapping of shape IDs to element IDs
            
        Returns:
            Dictionary with feedback data in JSON format
        """
        if element_mapping:
            self.element_mapping = element_mapping
        
        try:
            presentation = self.service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            feedback = {
                'presentation_id': presentation_id,
                'presentation_title': presentation.get('title', ''),
                'timestamp': time.time(),
                'slides': []
            }
            
            for slide_idx, slide in enumerate(presentation.get('slides', [])):
                slide_feedback = {
                    'slide_index': slide_idx,
                    'slide_id': slide['objectId'],
                    'elements': []
                }
                
                for element in slide.get('pageElements', []):
                    if 'shape' in element:
                        shape = element['shape']
                        shape_id = element['objectId']
                        
                        # Extract text content
                        text_content = ""
                        if 'text' in shape:
                            text_elements = shape['text'].get('textElements', [])
                            for te in text_elements:
                                if 'textRun' in te:
                                    text_content += te['textRun'].get('content', '')
                        
                        # Map to element_id if available
                        element_id = self.element_mapping.get(shape_id, shape_id)
                        
                        # Extract shape properties
                        shape_type = shape.get('shapeType', 'UNKNOWN')
                        
                        slide_feedback['elements'].append({
                            'element_id': element_id,
                            'shape_id': shape_id,
                            'shape_type': shape_type,
                            'text_content': text_content.strip(),
                            'has_text_changes': bool(text_content.strip())
                        })
                
                feedback['slides'].append(slide_feedback)
            
            return feedback
            
        except Exception as e:
            print(f"Error extracting feedback: {e}")
            return {'error': str(e)}
    
    def save_feedback(self, feedback: Dict, output_path: str):
        """
        Save feedback to JSON file.
        
        Args:
            feedback: Feedback dictionary
            output_path: Path to save JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, indent=2)
        print(f"✓ Feedback saved to: {output_path}")
    
    def _compare_feedback(self, old_feedback: Optional[Dict], new_feedback: Dict) -> Dict:
        """
        Compare two feedback dictionaries and return changes.
        
        Returns:
            Dictionary with change information
        """
        if old_feedback is None:
            return {
                'has_changes': True,
                'new_elements': len([e for s in new_feedback.get('slides', []) for e in s.get('elements', [])]),
                'changes': []
            }
        
        changes = []
        old_elements = {}
        
        # Build lookup of old elements by shape_id
        for slide in old_feedback.get('slides', []):
            for elem in slide.get('elements', []):
                old_elements[elem.get('shape_id')] = elem
        
        # Compare with new elements
        for slide in new_feedback.get('slides', []):
            slide_idx = slide.get('slide_index', 0)
            for elem in slide.get('elements', []):
                shape_id = elem.get('shape_id')
                element_id = elem.get('element_id')
                new_text = elem.get('text_content', '').strip()
                
                if shape_id in old_elements:
                    old_text = old_elements[shape_id].get('text_content', '').strip()
                    if old_text != new_text:
                        changes.append({
                            'element_id': element_id,
                            'shape_id': shape_id,
                            'slide_index': slide_idx,
                            'old_text': old_text,
                            'new_text': new_text,
                            'change_type': 'text_modified'
                        })
                else:
                    # New element
                    changes.append({
                        'element_id': element_id,
                        'shape_id': shape_id,
                        'slide_index': slide_idx,
                        'new_text': new_text,
                        'change_type': 'element_added'
                    })
        
        return {
            'has_changes': len(changes) > 0,
            'change_count': len(changes),
            'changes': changes
        }
    
    def monitor_presentation(self, presentation_id: str, 
                           output_path: str,
                           interval: int = 5,
                           max_iterations: Optional[int] = None,
                           verbose: bool = True):
        """
        Monitor presentation for changes and extract feedback periodically.
        
        Args:
            presentation_id: Google Slides presentation ID
            output_path: Path to save feedback JSON
            interval: Polling interval in seconds (default: 5)
            max_iterations: Maximum number of iterations (None for infinite)
            verbose: Show detailed output (default: True)
        """
        print("=" * 70)
        print("CONTINUOUS MONITORING MODE")
        print("=" * 70)
        print(f"Presentation ID: {presentation_id}")
        print(f"Polling interval: {interval} seconds")
        print(f"Output file: {output_path}")
        if max_iterations:
            print(f"Max iterations: {max_iterations}")
        else:
            print("Max iterations: Unlimited (Press Ctrl+C to stop)")
        print("=" * 70)
        print()
        
        iteration = 0
        last_feedback = None
        last_timestamp = None
        stats = {
            'total_checks': 0,
            'changes_detected': 0,
            'elements_modified': 0,
            'start_time': time.time()
        }
        
        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                stats['total_checks'] += 1
                
                # Show status
                current_time = time.strftime("%H:%M:%S")
                if verbose:
                    print(f"[{current_time}] Check #{iteration} - Extracting feedback...", end=' ', flush=True)
                
                try:
                    feedback = self.extract_feedback(presentation_id)
                    
                    if 'error' in feedback:
                        print(f"✗ Error: {feedback['error']}")
                        time.sleep(interval)
                        continue
                    
                    # Compare with previous feedback
                    comparison = self._compare_feedback(last_feedback, feedback)
                    
                    if comparison['has_changes']:
                        change_count = comparison.get('change_count', len(comparison.get('changes', [])))
                        
                        # Only count as change if there are actual modifications (not just first check)
                        if last_feedback is not None and change_count > 0:
                            stats['changes_detected'] += 1
                            stats['elements_modified'] += change_count
                            
                            # Save feedback
                            self.save_feedback(feedback, output_path)
                            
                            # Show changes
                            print("✓ CHANGES DETECTED!")
                            print(f"  → {change_count} change(s) found")
                            
                            if verbose:
                                for change in comparison.get('changes', []):
                                    if change['change_type'] == 'text_modified':
                                        print(f"    • Slide {change['slide_index'] + 1}: "
                                              f"'{change['element_id']}' "
                                              f"'{change['old_text']}' → '{change['new_text']}'")
                                    elif change['change_type'] == 'element_added':
                                        print(f"    • Slide {change['slide_index'] + 1}: "
                                              f"New element '{change['element_id']}' "
                                              f"('{change['new_text']}')")
                            
                            # Show statistics
                            elapsed = time.time() - stats['start_time']
                            print(f"\n  Statistics:")
                            print(f"    • Total checks: {stats['total_checks']}")
                            print(f"    • Changes detected: {stats['changes_detected']}")
                            print(f"    • Elements modified: {stats['elements_modified']}")
                            print(f"    • Monitoring time: {elapsed:.1f}s")
                            print()
                        else:
                            # First check - just save baseline
                            if verbose:
                                print("✓ Baseline established (first check)")
                            self.save_feedback(feedback, output_path)
                        
                        last_feedback = feedback
                        last_timestamp = feedback.get('timestamp')
                    else:
                        if verbose:
                            print("✓ No changes")
                        else:
                            print(".", end='', flush=True)
                    
                except Exception as e:
                    print(f"✗ Error during extraction: {e}")
                    if verbose:
                        import traceback
                        traceback.print_exc()
                
                # Wait before next check
                if iteration < (max_iterations or float('inf')):
                    if verbose:
                        print(f"  Waiting {interval} seconds until next check...\n")
                    time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 70)
            print("MONITORING STOPPED BY USER")
            print("=" * 70)
            elapsed = time.time() - stats['start_time']
            print(f"\nFinal Statistics:")
            print(f"  • Total checks: {stats['total_checks']}")
            print(f"  • Changes detected: {stats['changes_detected']}")
            print(f"  • Elements modified: {stats['elements_modified']}")
            print(f"  • Total monitoring time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
            print(f"  • Last feedback saved to: {output_path}")
            print("\n✓ Monitoring stopped gracefully")
            print("=" * 70)


def main():
    """CLI for feedback service."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract feedback from Google Slides presentation'
    )
    parser.add_argument('presentation_id', help='Google Slides presentation ID')
    parser.add_argument('--output', '-o', default='feedback.json',
                       help='Output JSON file path (default: feedback.json)')
    parser.add_argument('--mapping', '-m', type=str, default=None,
                       help='Path to element mapping JSON file')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor presentation for changes')
    parser.add_argument('--interval', type=int, default=5,
                       help='Polling interval in seconds (default: 5)')
    parser.add_argument('--max-iterations', type=int, default=None,
                       help='Maximum number of iterations (default: unlimited)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Quiet mode (less verbose output)')
    
    args = parser.parse_args()
    
    service = FeedbackService()
    print("Authenticating with Google Slides API...")
    service.authenticate()
    print("✓ Authentication successful\n")
    
    # Load element mapping if provided
    if args.mapping:
        service.load_element_mapping(args.mapping)
        print()
    
    if args.monitor:
        service.monitor_presentation(
            args.presentation_id,
            args.output,
            interval=args.interval,
            max_iterations=args.max_iterations,
            verbose=not args.quiet
        )
    else:
        print("Extracting feedback (one-time)...")
        feedback = service.extract_feedback(args.presentation_id)
        
        if 'error' in feedback:
            print(f"✗ Error: {feedback['error']}")
            sys.exit(1)
        
        service.save_feedback(feedback, args.output)
        
        # Count elements
        total_elements = sum(len(slide.get('elements', [])) for slide in feedback.get('slides', []))
        print(f"\n✓ Feedback extracted successfully")
        print(f"  • Slides processed: {len(feedback.get('slides', []))}")
        print(f"  • Total elements: {total_elements}")
        print(f"  • Saved to: {args.output}")
        print(f"\n💡 Tip: Use --monitor for continuous monitoring")


if __name__ == "__main__":
    main()


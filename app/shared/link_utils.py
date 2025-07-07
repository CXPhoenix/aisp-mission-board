"""
Link resolution utilities for safe handling of Beanie Link objects.
Provides defensive functions to handle broken links and data synchronization.
"""

from typing import List, Optional, TypeVar, Union
from beanie import Link, Document
from beanie.odm.documents import DocType

T = TypeVar('T', bound=Document)


async def safe_fetch_link(link: Optional[Link[T]]) -> Optional[T]:
    """
    Safely fetch a single Link object, returning None if the link is broken.
    
    Args:
        link: The Link object to fetch
        
    Returns:
        The resolved document or None if link is broken/None
    """
    if link is None:
        return None
    
    try:
        if hasattr(link, 'fetch'):
            resolved = await link.fetch()
            return resolved
        else:
            # Already resolved or direct object
            return link
    except Exception:
        # Link is broken or fetch failed
        return None


async def safe_fetch_links(links: List[Link[T]]) -> List[T]:
    """
    Safely fetch a list of Link objects, filtering out broken links.
    
    Args:
        links: List of Link objects to fetch
        
    Returns:
        List of resolved documents (broken links are filtered out)
    """
    if not links:
        return []
    
    resolved_items = []
    for link in links:
        resolved = await safe_fetch_link(link)
        if resolved is not None:
            resolved_items.append(resolved)
    
    return resolved_items


async def cleanup_broken_links(links: List[Link[T]]) -> List[Link[T]]:
    """
    Remove broken links from a list of Link objects.
    
    Args:
        links: List of Link objects to clean
        
    Returns:
        List of valid Link objects with broken links removed
    """
    if not links:
        return []
    
    valid_links = []
    for link in links:
        resolved = await safe_fetch_link(link)
        if resolved is not None:
            valid_links.append(link)
    
    return valid_links


async def validate_user_links(user) -> dict:
    """
    Validate all link references in a user object and return status.
    
    Args:
        user: User document with link fields
        
    Returns:
        Dictionary with validation results for each link field
    """
    validation_results = {
        'bag': {'total': 0, 'broken': 0, 'valid': 0},
        'ongoing_missions': {'total': 0, 'broken': 0, 'valid': 0},
        'completed_missions': {'total': 0, 'broken': 0, 'valid': 0},
        'review_pending_missions': {'total': 0, 'broken': 0, 'valid': 0}
    }
    
    # Check bag links
    if hasattr(user, 'bag') and user.bag:
        validation_results['bag']['total'] = len(user.bag)
        for bag_item in user.bag:
            if await safe_fetch_link(bag_item) is None:
                validation_results['bag']['broken'] += 1
            else:
                validation_results['bag']['valid'] += 1
    
    # Check ongoing missions
    if hasattr(user, 'ongoing_missions') and user.ongoing_missions:
        validation_results['ongoing_missions']['total'] = len(user.ongoing_missions)
        for mission in user.ongoing_missions:
            if await safe_fetch_link(mission) is None:
                validation_results['ongoing_missions']['broken'] += 1
            else:
                validation_results['ongoing_missions']['valid'] += 1
    
    # Check completed missions
    if hasattr(user, 'completed_missions') and user.completed_missions:
        validation_results['completed_missions']['total'] = len(user.completed_missions)
        for mission in user.completed_missions:
            if await safe_fetch_link(mission) is None:
                validation_results['completed_missions']['broken'] += 1
            else:
                validation_results['completed_missions']['valid'] += 1
    
    # Check review pending missions
    if hasattr(user, 'review_pending_missions') and user.review_pending_missions:
        validation_results['review_pending_missions']['total'] = len(user.review_pending_missions)
        for mission in user.review_pending_missions:
            if await safe_fetch_link(mission) is None:
                validation_results['review_pending_missions']['broken'] += 1
            else:
                validation_results['review_pending_missions']['valid'] += 1
    
    return validation_results
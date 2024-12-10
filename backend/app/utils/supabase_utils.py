from fastapi import HTTPException

def handle_supabase_response(response):
    """
    Handle the response from Supabase.

    Args:
        response: The response object from Supabase.

    Returns:
        A dict containing the data if present, otherwise raises an HTTPException.

    Raises:
        HTTPException: If the response data is empty or there's an error.
    """
    if not response.data:
        return {"message": "No data found", "data": []}

    return response.data

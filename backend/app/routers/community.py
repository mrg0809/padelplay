from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.connection import supabase
from app.core.security import get_current_user
from typing import Optional
from uuid import UUID
from datetime import datetime

router = APIRouter()


class FollowRequest(BaseModel):
    follower_id: UUID
    followed_id: UUID

class UnfollowRequest(BaseModel):
    follower_id: UUID
    followed_id: UUID

class ReactionRequest(BaseModel):
    post_id: UUID
    player_id: UUID
    reaction_type: str

class UnreactionRequest(BaseModel):
    post_id: UUID
    player_id: UUID

class CreatePostRequest(BaseModel):
    club_id: UUID
    content: str
    media_url: Optional[str] = None

class DeletePostRequest(BaseModel):
    club_id: UUID

# Endpoint para seguir a un usuario
@router.post("/follow")
async def follow_user(request: FollowRequest, current_user=Depends(get_current_user)):
    try:
        # Insertar en la tabla follows
        response = supabase.table("follows").insert({
            "follower_id": str(request.follower_id),
            "followed_id": str(request.followed_id),
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return {"message": "Ahora sigues a este usuario.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para dejar de seguir a un usuario
@router.delete("/unfollow")
async def unfollow_user(request: UnfollowRequest, current_user=Depends(get_current_user)):
    try:
        # Eliminar de la tabla follows
        response = supabase.table("follows").delete().eq("follower_id", str(request.follower_id)).eq("followed_id", str(request.followed_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="No se encontró el registro de seguimiento.")

        return {"message": "Has dejado de seguir a este usuario.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Endpoint para reaccionar a un post
@router.post("/react")
async def react_to_post(request: ReactionRequest, current_user=Depends(get_current_user)):
    try:
        # Insertar en la tabla reactions
        response = supabase.table("reactions").insert({
            "post_id": str(request.post_id),
            "player_id": str(request.player_id),
            "reaction_type": request.reaction_type,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return {"message": "Reacción registrada.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para eliminar una reacción
@router.delete("/unreact")
async def unreact_to_post(request: UnreactionRequest, current_user=Depends(get_current_user)):
    try:
        # Eliminar de la tabla reactions
        response = supabase.table("reactions").delete().eq("post_id", str(request.post_id)).eq("player_id", str(request.player_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="No se encontró la reacción.")

        return {"message": "Reacción eliminada.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# Endpoint para publicar un post
@router.post("/posts")
async def create_post(request: CreatePostRequest, current_user=Depends(get_current_user)):
    try:
        # Insertar en la tabla posts
        response = supabase.table("posts").insert({
            "club_id": str(request.club_id),
            "content": request.content,
            "media_url": request.media_url,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

        return {"message": "Post publicado exitosamente.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Endpoint para borrar un post
@router.delete("/posts/{post_id}")
async def delete_post(post_id: UUID, request: DeletePostRequest, current_user=Depends(get_current_user)):
    try:
        # Verificar que el post pertenece al club
        post = supabase.table("posts").select("*").eq("id", str(post_id)).eq("club_id", str(request.club_id)).execute()

        if not post.data:
            raise HTTPException(status_code=404, detail="Post no encontrado o no tienes permisos para eliminarlo.")

        # Eliminar el post
        response = supabase.table("posts").delete().eq("id", str(post_id)).execute()

        return {"message": "Post eliminado exitosamente.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Endpoint para obtener los posts de un club
@router.get("/posts/club/{club_id}")
async def get_posts_by_club(club_id: UUID, current_user=Depends(get_current_user)):
    try:
        # Obtener los posts del club
        posts = supabase.table("posts").select("*").eq("club_id", str(club_id)).order("created_at", desc=True).execute()

        # Obtener reacciones para cada post
        posts_with_reactions = []
        for post in posts.data:
            reactions = supabase.table("reactions").select("reaction_type").eq("post_id", post["id"]).execute()
            reaction_counts = {}
            for reaction in reactions.data:
                reaction_counts[reaction["reaction_type"]] = reaction_counts.get(reaction["reaction_type"], 0) + 1
            post["reactions"] = reaction_counts
            posts_with_reactions.append(post)

        return {"posts": posts_with_reactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
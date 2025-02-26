-- This is the SQL function that should be added to your Supabase project
-- to handle the followers and following arrays in the profiles table

CREATE OR REPLACE FUNCTION update_follow_arrays()
RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'INSERT') THEN
    -- Update the followers array for the followed user
    UPDATE profiles
    SET followers = array_append(followers, NEW.follower_id)
    WHERE id = NEW.followed_id;
    
    -- Update the following array for the follower user
    UPDATE profiles
    SET following = array_append(following, NEW.followed_id)
    WHERE id = NEW.follower_id;
    
    RETURN NEW;
  ELSIF (TG_OP = 'DELETE') THEN
    -- Remove from followers array
    UPDATE profiles
    SET followers = array_remove(followers, OLD.follower_id)
    WHERE id = OLD.followed_id;
    
    -- Remove from following array
    UPDATE profiles
    SET following = array_remove(following, OLD.followed_id)
    WHERE id = OLD.follower_id;
    
    RETURN OLD;
  END IF;
  
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

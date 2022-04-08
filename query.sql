select
    post_id,
    text,
    topic,
    forum_id,
    case
        when (birth_year % 10) in (0, 1) then 'test'
        else 'train'
    end as partition
from posts
left join subforums using (forum_id)
left join users using (user_id)

--load users from tweet table
INSERT INTO twitter_coaid.user (userID,status,content)
SELECT a.author_id as userID , 'Reload' as status, '' as content FROM 
(SELECT DISTINCT author_id FROM twitter_coaid.tweet WHERE author_id NOT IN (
SELECT DISTINCT userID FROM twitter_coaid.user ) AND author_id != 0) a
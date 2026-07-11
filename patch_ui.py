import re

# 1. Update index.html
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Reduce blurs
    html = html.replace('backdrop-filter: blur(8px)', 'backdrop-filter: blur(3px)')
    html = html.replace('filter: blur(100px)', 'filter: blur(40px)')
    
    # Update play-btn hover logic (ensure it stays visible when hovered, maybe make it scale)
    if '.video-card:hover .thumb .play-btn { opacity:1; }' in html:
        html = html.replace('.video-card:hover .thumb .play-btn { opacity:1; }', '.video-card:hover .thumb .play-btn { opacity:1; transform:translate(-50%,-50%) scale(1.1); z-index:10; }')
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
except Exception as e:
    print(f"Error updating index.html: {e}")

# 2. Update temp.js
try:
    with open('temp.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # Add toggle like and share functions
    extra_funcs = """
window.toggleLike = async function(btn, videoId) {
    const isLiked = localStorage.getItem('liked_' + videoId);
    try {
        if (isLiked) {
            await apiFetch(`/videos/${videoId}/unlike`, {method: 'POST'});
            localStorage.removeItem('liked_' + videoId);
            btn.innerHTML = '&#9825; Thích';
            btn.classList.remove('btn-purple');
            btn.classList.add('btn-outline');
        } else {
            await apiFetch(`/videos/${videoId}/like`, {method: 'POST'});
            localStorage.setItem('liked_' + videoId, 'true');
            btn.innerHTML = '&#10084; Đã thích';
            btn.classList.remove('btn-outline');
            btn.classList.add('btn-purple');
        }
    } catch(e) {
        toast('Lỗi: ' + e.message, 'error');
    }
}

window.shareVideo = function(videoId) {
    const url = window.location.origin + window.location.pathname + '#/video/' + videoId;
    navigator.clipboard.writeText(url).then(() => {
        toast('Đã sao chép liên kết video!');
    }).catch(err => {
        toast('Không thể sao chép liên kết!', 'error');
    });
}

window.delComment = async function(videoId, commentId) {
    if(!confirm('Bạn có chắc chắn muốn xóa bình luận này?')) return;
    try {
        await apiFetch(`/videos/${videoId}/comments/${commentId}`, {method: 'DELETE'});
        toast('Đã xóa bình luận!');
        const el = document.getElementById('comment-' + commentId);
        if(el) el.remove();
    } catch(e) {
        toast('Lỗi xóa bình luận: ' + e.message, 'error');
    }
}
"""
    if 'window.toggleLike =' not in js:
        js += '\n' + extra_funcs

    # Replace like button and share button in renderVideo
    # We don't have the exact substring but we can use regex
    # find something like <button class="btn btn-outline" style="flex:1">&#9825; Thích</button>
    js = re.sub(
        r'<button class="btn btn-outline" style="flex:1">&#9825; Thích</button>',
        r'''<button class="btn ${localStorage.getItem('liked_'+video.id)?'btn-purple':'btn-outline'}" style="flex:1" onclick="toggleLike(this, '${video.id}')">${localStorage.getItem('liked_'+video.id)?'&#10084; Đã thích':'&#9825; Thích'}</button>''',
        js
    )
    js = re.sub(
        r'<button class="btn btn-outline" style="flex:1">&#10150; Chia sẻ</button>',
        r'''<button class="btn btn-outline" style="flex:1" onclick="shareVideo('${video.id}')">&#10150; Chia sẻ</button>''',
        js
    )

    # Object fit cover for main image in renderVideo
    js = js.replace(
        'loading="eager" decoding="async" fetchpriority="high"/>',
        'loading="eager" decoding="async" fetchpriority="high" style="width:100%;height:auto;max-height:80vh;object-fit:cover;border-radius:12px;border:1px solid var(--neon-purple);box-shadow:0 0 20px rgba(188,19,254,0.15)"/>'
    )
    
    # Add delete button to comments
    # The comment render loop looks like this (from earlier context if any, or we can find it)
    # let's find the comment template
    comment_pattern = r'(\<div class="comment-content"\>\s*\<div class="comment-author"\>.*?\<\/div\>\s*\<div class="comment-text"\>\s*\$\{esc\(c\.content\)\}\s*\<\/div\>\s*\<div class="comment-date"\>\s*\$\{dateStr\(c\.created_at\)\}\s*\<\/div\>\s*\<\/div\>)'
    
    def repl_comment(m):
        content = m.group(1)
        del_btn = r'''${(currentUser && (currentUser.id === c.user_id || currentUser.role === 'ADMIN')) ? `<button onclick="delComment('${video.id}', '${c.id}')" style="background:none;border:none;color:var(--red);cursor:pointer;position:absolute;top:10px;right:10px;font-size:1.1rem" title="Xóa">&#128465;</button>` : ''}'''
        return content + '\n' + del_btn

    js = re.sub(comment_pattern, repl_comment, js)
    
    # Since we added position absolute, we need position relative on comment
    js = js.replace('<div class="comment" style="display:flex;gap:12px">', '<div class="comment" id="comment-${c.id}" style="display:flex;gap:12px;position:relative">')

    # Fix object-fit cover in Quick View modal
    js = js.replace('object-fit:contain;', 'object-fit:cover;width:100%;height:100%;')

    with open('temp.js', 'w', encoding='utf-8') as f:
        f.write(js)
        
    print("Updated temp.js successfully")

except Exception as e:
    print(f"Error updating temp.js: {e}")

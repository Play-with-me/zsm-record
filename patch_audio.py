import re

with open('temp.js', 'r', encoding='utf-8') as f:
    js = f.read()

old_toggleLike = '''window.toggleLike = async function(btn, videoId) {
      const isLiked = localStorage.getItem('liked_' + videoId);
      try {
          const countSpan = document.getElementById('like-count');'''

new_toggleLike = '''function playSound(type) {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gainNode = ctx.createGain();
        osc.type = 'sine';
        if (type === 'like') {
            osc.frequency.setValueAtTime(600, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.1);
        } else {
            osc.frequency.setValueAtTime(400, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.1);
        }
        gainNode.gain.setValueAtTime(0.1, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
        osc.connect(gainNode);
        gainNode.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.1);
    } catch(e) {}
}

window.toggleLike = async function(btn, videoId) {
      const isLiked = localStorage.getItem('liked_' + videoId);
      playSound(isLiked ? 'unlike' : 'like');
      try {
          const countSpan = document.getElementById('like-count');'''

js = js.replace(old_toggleLike, new_toggleLike)

with open('temp.js', 'w', encoding='utf-8') as f:
    f.write(js)

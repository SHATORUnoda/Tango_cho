"""
単語帳アプリ - Flask版
起動: python app.py
ブラウザで http://localhost:3000 を開く
"""

from flask import Flask, render_template_string, jsonify, request
import json, os

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "words.json")

def load_words():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_words(words):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

HTML = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>単語帳</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0e0e10;
    --surface: #18181b;
    --surface2: #232329;
    --border: rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.15);
    --text: #f0eee8;
    --muted: #888;
    --accent: #c8f060;
    --accent-dim: rgba(200,240,96,0.12);
    --danger: #ff5c5c;
    --danger-dim: rgba(255,92,92,0.12);
    --info: #60b8f0;
    --info-dim: rgba(96,184,240,0.12);
    --radius: 12px;
    --radius-sm: 8px;
  }
  body { background:var(--bg); color:var(--text); font-family:'Noto Sans JP',sans-serif; min-height:100vh; display:flex; flex-direction:column; }

  header { padding:1.25rem 2rem; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; gap:1rem; }
  .logo { font-family:'Syne',sans-serif; font-weight:800; font-size:1.3rem; letter-spacing:-0.02em; color:var(--accent); }
  .logo span { color:var(--text); font-weight:400; }
  .header-stats { display:flex; gap:1.5rem; font-size:.8rem; color:var(--muted); }
  .header-stats strong { color:var(--text); }

  main { flex:1; display:grid; grid-template-columns:280px 1fr; }

  aside { border-right:1px solid var(--border); padding:1.5rem 1rem; display:flex; flex-direction:column; gap:.5rem; overflow-y:auto; max-height:calc(100vh - 64px); }
  .aside-label { font-family:'Syne',sans-serif; font-size:.68rem; font-weight:700; letter-spacing:.12em; color:var(--muted); text-transform:uppercase; padding:.5rem .75rem .25rem; }
  .word-item { display:flex; align-items:center; justify-content:space-between; padding:.6rem .75rem; border-radius:var(--radius-sm); cursor:pointer; border:1px solid transparent; transition:all .15s; gap:.5rem; }
  .word-item:hover { background:var(--surface2); }
  .word-item.active { background:var(--accent-dim); border-color:rgba(200,240,96,.3); }
  .wi-en { font-family:'Syne',sans-serif; font-weight:600; font-size:.9rem; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .wi-badge { font-size:.7rem; padding:2px 7px; border-radius:20px; background:var(--surface2); color:var(--muted); border:1px solid var(--border); min-width:36px; text-align:center; white-space:nowrap; }
  .wi-badge.has-count { background:var(--accent-dim); color:var(--accent); border-color:rgba(200,240,96,.3); }

  .content { display:flex; flex-direction:column; overflow:hidden; }
  .tabs { display:flex; border-bottom:1px solid var(--border); padding:0 2rem; }
  .tab { padding:1rem 1.25rem; font-size:.85rem; font-weight:500; color:var(--muted); cursor:pointer; border-bottom:2px solid transparent; transition:all .15s; background:none; border-top:none; border-left:none; border-right:none; }
  .tab:hover { color:var(--text); }
  .tab.active { color:var(--accent); border-bottom-color:var(--accent); }

  .panel { display:none; flex:1; padding:2rem; overflow-y:auto; }
  .panel.active { display:flex; flex-direction:column; gap:1.5rem; }

  /* empty state */
  .empty-state { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1rem; padding:4rem 2rem; color:var(--muted); text-align:center; }
  .empty-state .big { font-size:3rem; }
  .empty-state p { font-size:.9rem; line-height:1.7; }

  /* Flash */
  .flash-area { display:flex; flex-direction:column; align-items:center; gap:1.5rem; }
  .card-wrap { perspective:1200px; width:100%; max-width:520px; height:220px; cursor:pointer; }
  .card-inner { position:relative; width:100%; height:100%; transform-style:preserve-3d; transition:transform .55s cubic-bezier(.4,0,.2,1); }
  .card-inner.flipped { transform:rotateY(180deg); }
  .card-face { position:absolute; width:100%; height:100%; backface-visibility:hidden; -webkit-backface-visibility:hidden; background:var(--surface); border:1px solid var(--border2); border-radius:var(--radius); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.75rem; padding:1.5rem; }
  .card-back { transform:rotateY(180deg); }
  .card-lang { font-family:'Syne',sans-serif; font-size:.68rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:var(--muted); }
  .card-word { font-family:'Syne',sans-serif; font-size:1.9rem; font-weight:700; color:var(--text); text-align:center; }
  .card-hint { font-size:.78rem; color:var(--muted); }
  .card-ja { font-size:1.3rem; font-weight:700; color:var(--accent); text-align:center; white-space:pre-line; line-height:1.6; }
  .card-count-label { font-size:.78rem; color:var(--muted); }

  .flash-controls { display:flex; align-items:center; gap:.75rem; flex-wrap:wrap; justify-content:center; }
  .flash-progress { font-family:'Syne',sans-serif; font-size:.85rem; color:var(--muted); min-width:60px; text-align:center; }
  .memorized-btn { padding:.65rem 1.5rem; background:var(--accent); color:#000; border:none; border-radius:var(--radius-sm); font-weight:700; font-size:.9rem; cursor:pointer; transition:all .15s; font-family:'Syne',sans-serif; }
  .memorized-btn:hover { opacity:.85; transform:scale(1.02); }
  .memorized-btn:active { transform:scale(.97); }

  .btn { padding:.55rem 1.1rem; background:transparent; color:var(--text); border:1px solid var(--border2); border-radius:var(--radius-sm); font-size:.82rem; cursor:pointer; transition:all .15s; font-family:'Noto Sans JP',sans-serif; }
  .btn:hover { background:var(--surface2); }
  .btn:active { transform:scale(.97); }
  .btn-danger { border-color:var(--danger); color:var(--danger); }
  .btn-danger:hover { background:var(--danger-dim); }
  .btn-info { border-color:var(--info); color:var(--info); }
  .btn-info:hover { background:var(--info-dim); }
  .btn-accent { background:var(--accent-dim); border-color:rgba(200,240,96,.3); color:var(--accent); }
  .btn-accent:hover { background:rgba(200,240,96,.2); }

  .list-table { width:100%; border-collapse:collapse; font-size:.9rem; }
  .list-table th { font-family:'Syne',sans-serif; font-size:.7rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); padding:.75rem 1rem; text-align:left; border-bottom:1px solid var(--border); }
  .list-table td { padding:.8rem 1rem; border-bottom:1px solid var(--border); vertical-align:middle; }
  .list-table tr:hover td { background:var(--surface2); }
  .count-cell { font-family:'Syne',sans-serif; font-weight:700; color:var(--accent); min-width:60px; }
  .td-actions { display:flex; gap:.5rem; }

  .form-group { display:flex; flex-direction:column; gap:.4rem; max-width:560px; }
  .form-group label { font-size:.8rem; color:var(--muted); font-weight:500; }
  .form-group input, .form-group textarea { background:var(--surface); border:1px solid var(--border2); border-radius:var(--radius-sm); color:var(--text); padding:.65rem .9rem; font-size:.9rem; font-family:'Noto Sans JP',sans-serif; outline:none; transition:border-color .15s; }
  .form-group input:focus, .form-group textarea:focus { border-color:var(--accent); }
  .form-group textarea { resize:vertical; min-height:80px; }
  .form-row { display:flex; gap:1rem; flex-wrap:wrap; }
  .form-row .form-group { flex:1; min-width:180px; }

  .io-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; }
  .io-card { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:1.5rem; display:flex; flex-direction:column; gap:1rem; }
  .io-card h3 { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; }
  .io-card p { font-size:.82rem; color:var(--muted); line-height:1.6; }
  .drop-zone { border:2px dashed var(--border2); border-radius:var(--radius-sm); padding:2rem; text-align:center; color:var(--muted); font-size:.85rem; cursor:pointer; transition:all .15s; }
  .drop-zone:hover, .drop-zone.drag-over { border-color:var(--accent); color:var(--accent); background:var(--accent-dim); }

  #toast { position:fixed; bottom:2rem; left:50%; transform:translateX(-50%) translateY(80px); background:var(--surface2); border:1px solid var(--border2); border-radius:var(--radius-sm); padding:.7rem 1.5rem; font-size:.85rem; color:var(--text); opacity:0; transition:all .3s; z-index:9999; white-space:nowrap; }
  #toast.show { opacity:1; transform:translateX(-50%) translateY(0); }

  .modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,.6); align-items:center; justify-content:center; z-index:1000; }
  .modal-overlay.open { display:flex; }
  .modal { background:var(--surface); border:1px solid var(--border2); border-radius:var(--radius); padding:2rem; width:440px; max-width:90vw; display:flex; flex-direction:column; gap:1.25rem; }
  .modal h3 { font-family:'Syne',sans-serif; font-weight:700; }
  .modal-actions { display:flex; justify-content:flex-end; gap:.75rem; }

  .section-title { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:var(--text); }
</style>
</head>
<body>

<header>
  <div class="logo">単語帳<span> / Cards</span></div>
  <div class="header-stats">
    <span>単語数: <strong id="stat-total">0</strong></span>
    <span>累計記憶: <strong id="stat-mem">0</strong></span>
  </div>
</header>

<main>
  <aside>
    <div class="aside-label">用語一覧</div>
    <div id="word-list"></div>
  </aside>

  <div class="content">
    <div class="tabs">
      <button class="tab active" onclick="switchTab('flash')">フラッシュカード</button>
      <button class="tab" onclick="switchTab('list')">リスト</button>
      <button class="tab" onclick="switchTab('add')">追加・編集</button>
      <button class="tab" onclick="switchTab('io')">インポート / エクスポート</button>
    </div>

    <!-- Flash panel -->
    <div class="panel active" id="panel-flash">
      <div class="flash-area" id="flash-area">
        <div class="card-wrap" onclick="flipCard()">
          <div class="card-inner" id="card-inner">
            <div class="card-face">
              <span class="card-lang">用語</span>
              <span class="card-word" id="f-front">-</span>
              <span class="card-hint">クリックで答えを確認</span>
            </div>
            <div class="card-face card-back">
              <span class="card-lang">説明・答え</span>
              <span class="card-ja" id="f-back">-</span>
              <span class="card-count-label" id="f-count">覚えた回数: 0</span>
            </div>
          </div>
        </div>
        <div class="flash-controls">
          <button class="btn" onclick="prevCard()">← 前へ</button>
          <span class="flash-progress" id="f-progress">0 / 0</span>
          <button class="btn" onclick="nextCard()">次へ →</button>
        </div>
        <div class="flash-controls">
          <button class="memorized-btn" onclick="markMemorized()">✓ 覚えた！</button>
          <button class="btn btn-accent" onclick="shuffleDeck()">シャッフル</button>
          <button class="btn" onclick="resetDeck()">最初から</button>
        </div>
      </div>
      <div class="empty-state" id="flash-empty" style="display:none;">
        <div class="big">📭</div>
        <p>まだ用語がありません。<br>「追加・編集」タブまたはCSVインポートから追加してください。</p>
        <button class="btn btn-accent" onclick="switchTab('add')">用語を追加する</button>
      </div>
    </div>

    <!-- List panel -->
    <div class="panel" id="panel-list">
      <div style="display:flex;gap:.75rem;align-items:center;flex-wrap:wrap;">
        <span class="section-title">全用語リスト</span>
        <button class="btn" onclick="sortList('front')">用語順</button>
        <button class="btn" onclick="sortList('count')">記憶回数順</button>
        <button class="btn btn-danger" onclick="confirmResetAll()">回数リセット</button>
      </div>
      <table class="list-table">
        <thead><tr><th>#</th><th>用語</th><th>説明・答え</th><th>覚えた回数</th><th>操作</th></tr></thead>
        <tbody id="list-body"></tbody>
      </table>
    </div>

    <!-- Add/Edit panel -->
    <div class="panel" id="panel-add">
      <span class="section-title">用語を追加</span>
      <div class="form-row">
        <div class="form-group">
          <label>用語（表面）</label>
          <input type="text" id="add-front" placeholder="例: 享保の改革">
        </div>
        <div class="form-group">
          <label>説明・答え（裏面）</label>
          <textarea id="add-back" placeholder="例: 徳川吉宗が行った改革&#10;倹約令・新田開発など"></textarea>
        </div>
      </div>
      <div><button class="btn btn-accent" onclick="addWord()">追加する</button></div>

      <hr style="border:none;border-top:1px solid var(--border);margin-top:.5rem;">
      <span class="section-title">用語を編集</span>
      <p style="font-size:.82rem;color:var(--muted)">サイドバーまたはリストの「編集」ボタンから選択してください。</p>
      <div id="edit-area" style="display:none;flex-direction:column;gap:1rem;">
        <div class="form-row">
          <div class="form-group">
            <label>用語（表面）</label>
            <input type="text" id="edit-front">
          </div>
          <div class="form-group">
            <label>説明・答え（裏面）</label>
            <textarea id="edit-back"></textarea>
          </div>
        </div>
        <div style="display:flex;gap:.75rem;">
          <button class="btn btn-accent" onclick="saveEdit()">保存</button>
          <button class="btn" onclick="cancelEdit()">キャンセル</button>
          <button class="btn btn-danger" onclick="deleteSelected()">削除</button>
        </div>
      </div>
    </div>

    <!-- IO panel -->
    <div class="panel" id="panel-io">
      <div class="io-grid">
        <div class="io-card">
          <h3>📤 エクスポート</h3>
          <p>現在の用語帳をCSVまたはJSONで保存します。記憶回数も含まれます。<br><br>CSVの列: <code style="color:var(--accent);font-size:.78rem">FrontText, BackText, Count</code></p>
          <div style="display:flex;gap:.75rem;flex-wrap:wrap;">
            <button class="btn btn-accent" onclick="exportCSV()">CSVでダウンロード</button>
            <button class="btn" onclick="exportJSON()">JSONでダウンロード</button>
          </div>
        </div>
        <div class="io-card">
          <h3>📥 インポート</h3>
          <p>CSVファイルをインポートします。<br>必要な列: <code style="color:var(--accent);font-size:.78rem">FrontText, BackText</code><br>（en/ja 列名も対応）</p>
          <div class="drop-zone" id="drop-zone" onclick="document.getElementById('file-input').click()"
               ondragover="onDragOver(event)" ondragleave="onDragLeave(event)" ondrop="onDrop(event)">
            ここにCSVをドロップ<br>またはクリックして選択
          </div>
          <input type="file" id="file-input" accept=".csv,.json" style="display:none" onchange="onFileSelect(event)">
          <div style="display:flex;gap:.5rem;align-items:center;">
            <label style="font-size:.8rem;color:var(--muted);">インポート時:</label>
            <select id="import-mode" style="background:var(--surface2);border:1px solid var(--border2);border-radius:var(--radius-sm);color:var(--text);padding:.4rem .7rem;font-size:.8rem;">
              <option value="merge">既存に追加（重複スキップ）</option>
              <option value="replace">既存を置き換え</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  </div>
</main>

<div id="toast"></div>

<div class="modal-overlay" id="edit-modal">
  <div class="modal">
    <h3>用語を編集</h3>
    <div class="form-group"><label>用語（表面）</label><input type="text" id="modal-front"></div>
    <div class="form-group"><label>説明・答え（裏面）</label><textarea id="modal-back"></textarea></div>
    <div class="modal-actions">
      <button class="btn btn-danger" onclick="deleteModalWord()">削除</button>
      <button class="btn" onclick="closeModal()">キャンセル</button>
      <button class="btn btn-accent" onclick="saveModalWord()">保存</button>
    </div>
  </div>
</div>

<script>
let words = [], deck = [], deckIdx = 0, flipped = false, editId = null, sortKey = null, sortAsc = true;

async function api(path, opts={}) {
  const r = await fetch(path, {headers:{'Content-Type':'application/json'}, ...opts});
  return r.json();
}

async function loadWords() {
  words = await api('/api/words');
  refreshAll();
}

function refreshAll() { renderSidebar(); renderList(); updateStats(); updateFlashEmpty(); }

function updateStats() {
  document.getElementById('stat-total').textContent = words.length;
  document.getElementById('stat-mem').textContent = words.reduce((s,w)=>s+w.count,0);
}

function updateFlashEmpty() {
  const empty = words.length === 0;
  document.getElementById('flash-area').style.display = empty ? 'none' : 'flex';
  document.getElementById('flash-empty').style.display = empty ? 'flex' : 'none';
}

function renderSidebar() {
  document.getElementById('word-list').innerHTML = words.map(w=>`
    <div class="word-item${editId===w.id?' active':''}" onclick="selectWord(${w.id})">
      <span class="wi-en">${w.front}</span>
      <span class="wi-badge${w.count>0?' has-count':''}">${w.count}</span>
    </div>`).join('');
}

function renderList() {
  let sorted = [...words];
  if (sortKey==='front') sorted.sort((a,b)=>sortAsc?a.front.localeCompare(b.front,'ja'):b.front.localeCompare(a.front,'ja'));
  if (sortKey==='count') sorted.sort((a,b)=>sortAsc?a.count-b.count:b.count-a.count);
  document.getElementById('list-body').innerHTML = sorted.length===0
    ? `<tr><td colspan="5" style="text-align:center;color:var(--muted);padding:2rem">用語がありません</td></tr>`
    : sorted.map((w,i)=>`
    <tr>
      <td style="color:var(--muted);font-size:.8rem">${i+1}</td>
      <td style="font-weight:600">${w.front}</td>
      <td style="color:var(--muted);white-space:pre-line;font-size:.85rem">${w.back}</td>
      <td class="count-cell">${w.count} 回</td>
      <td class="td-actions">
        <button class="btn" onclick="openModal(${w.id})">編集</button>
        <button class="btn btn-danger" onclick="confirmDelete(${w.id})">削除</button>
      </td>
    </tr>`).join('');
}

function sortList(key) {
  if (sortKey===key) sortAsc=!sortAsc; else { sortKey=key; sortAsc=true; }
  renderList();
}

// --- Flash ---
function buildDeck() {
  deck=[...words]; deckIdx=0; flipped=false; renderCard();
}
function renderCard() {
  if (!deck.length) return;
  const w=deck[deckIdx];
  document.getElementById('f-front').textContent=w.front;
  document.getElementById('f-back').textContent=w.back;
  document.getElementById('f-count').textContent=`覚えた回数: ${w.count}`;
  document.getElementById('f-progress').textContent=`${deckIdx+1} / ${deck.length}`;
  document.getElementById('card-inner').classList.remove('flipped');
  flipped=false;
}
function flipCard() {
  flipped=!flipped;
  document.getElementById('card-inner').classList.toggle('flipped',flipped);
}
function nextCard() { deckIdx=(deckIdx+1)%deck.length; renderCard(); }
function prevCard() { deckIdx=(deckIdx-1+deck.length)%deck.length; renderCard(); }
function shuffleDeck() { deck.sort(()=>Math.random()-.5); deckIdx=0; renderCard(); toast('シャッフルしました'); }
function resetDeck() { buildDeck(); toast('最初からスタート'); }

async function markMemorized() {
  if (!deck.length) return;
  const w=deck[deckIdx];
  const updated=await api(`/api/words/${w.id}/increment`,{method:'POST'});
  const idx=words.findIndex(x=>x.id===w.id);
  if (idx>=0) { words[idx].count=updated.count; deck[deckIdx].count=updated.count; }
  document.getElementById('f-count').textContent=`覚えた回数: ${updated.count}`;
  renderSidebar(); updateStats();
  toast(`「${w.front}」を記憶！ (${updated.count}回目)`);
  setTimeout(nextCard, 400);
}

// --- Add ---
async function addWord() {
  const front=document.getElementById('add-front').value.trim();
  const back=document.getElementById('add-back').value.trim();
  if (!front||!back) { toast('用語と説明を入力してください'); return; }
  const w=await api('/api/words',{method:'POST',body:JSON.stringify({front,back})});
  words.push(w);
  document.getElementById('add-front').value='';
  document.getElementById('add-back').value='';
  refreshAll(); buildDeck(); toast(`「${front}」を追加しました`);
}

// --- Edit (sidebar) ---
function selectWord(id) {
  editId=id;
  const w=words.find(x=>x.id===id);
  if (!w) return;
  document.getElementById('edit-front').value=w.front;
  document.getElementById('edit-back').value=w.back;
  document.getElementById('edit-area').style.display='flex';
  switchTab('add'); renderSidebar();
}
async function saveEdit() {
  const front=document.getElementById('edit-front').value.trim();
  const back=document.getElementById('edit-back').value.trim();
  if (!front||!back) return;
  await api(`/api/words/${editId}`,{method:'PUT',body:JSON.stringify({front,back})});
  const idx=words.findIndex(x=>x.id===editId);
  if (idx>=0) { words[idx].front=front; words[idx].back=back; }
  cancelEdit(); refreshAll(); buildDeck(); toast('保存しました');
}
function cancelEdit() {
  editId=null;
  document.getElementById('edit-area').style.display='none';
  renderSidebar();
}
async function deleteSelected() {
  if (!editId) return;
  await api(`/api/words/${editId}`,{method:'DELETE'});
  words=words.filter(x=>x.id!==editId);
  cancelEdit(); refreshAll(); buildDeck(); toast('削除しました');
}

// --- Modal edit ---
function openModal(id) {
  editId=id;
  const w=words.find(x=>x.id===id);
  document.getElementById('modal-front').value=w.front;
  document.getElementById('modal-back').value=w.back;
  document.getElementById('edit-modal').classList.add('open');
}
function closeModal() { document.getElementById('edit-modal').classList.remove('open'); editId=null; }
async function saveModalWord() {
  const front=document.getElementById('modal-front').value.trim();
  const back=document.getElementById('modal-back').value.trim();
  if (!front||!back) return;
  await api(`/api/words/${editId}`,{method:'PUT',body:JSON.stringify({front,back})});
  const idx=words.findIndex(x=>x.id===editId);
  if (idx>=0) { words[idx].front=front; words[idx].back=back; }
  closeModal(); refreshAll(); buildDeck(); toast('保存しました');
}
async function deleteModalWord() {
  await api(`/api/words/${editId}`,{method:'DELETE'});
  words=words.filter(x=>x.id!==editId);
  closeModal(); refreshAll(); buildDeck(); toast('削除しました');
}

function confirmDelete(id) {
  const w=words.find(x=>x.id===id);
  if (confirm(`「${w.front}」を削除しますか？`)) { editId=id; deleteSelected(); }
}
function confirmResetAll() {
  if (confirm('全用語の記憶回数をリセットしますか？')) resetAllCounts();
}
async function resetAllCounts() {
  await api('/api/words/reset_counts',{method:'POST'});
  words.forEach(w=>w.count=0);
  refreshAll(); buildDeck(); toast('全リセット完了');
}

// --- Export ---
function exportCSV() {
  let csv='FrontText,BackText,Count\n';
  words.forEach(w=>{ csv+=`"${w.front}","${w.back}",${w.count}\n`; });
  download('tangocho.csv', csv, 'text/csv');
}
function exportJSON() {
  download('tangocho.json', JSON.stringify(words,null,2), 'application/json');
}
function download(name, content, type) {
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([content],{type}));
  a.download=name; a.click();
  toast(`${name} をダウンロードしました`);
}

// --- Import ---
function onDragOver(e) { e.preventDefault(); document.getElementById('drop-zone').classList.add('drag-over'); }
function onDragLeave() { document.getElementById('drop-zone').classList.remove('drag-over'); }
function onDrop(e) {
  e.preventDefault();
  document.getElementById('drop-zone').classList.remove('drag-over');
  const file=e.dataTransfer.files[0]; if (file) processFile(file);
}
function onFileSelect(e) { if (e.target.files[0]) processFile(e.target.files[0]); }

async function processFile(file) {
  const text=await file.text();
  const mode=document.getElementById('import-mode').value;
  const ext=file.name.split('.').pop().toLowerCase();
  let data;
  if (ext==='json') {
    try { data=JSON.parse(text); } catch { toast('JSONのパースに失敗しました'); return; }
    // JSON形式の変換 (front/back or en/ja or FrontText/BackText)
    data=data.map(item=>({
      front: item.front||item.en||item.FrontText||'',
      back:  item.back||item.ja||item.BackText||'',
      count: parseInt(item.count||0)
    }));
  } else {
    data=parseCSV(text);
  }
  if (!data||!data.length) { toast('データが見つかりませんでした'); return; }
  const result=await api('/api/words/import',{method:'POST',body:JSON.stringify({words:data,mode})});
  words=result.words;
  refreshAll(); buildDeck();
  toast(`${result.added}語を追加しました（${result.skipped}語スキップ）`);
}

function parseCSV(text) {
  const lines=text.trim().split('\n');
  if (!lines.length) return [];
  const splitCSV=line=>{
    const cols=[]; let cur='', inQ=false;
    for (let c of line) {
      if (c==='"') inQ=!inQ;
      else if (c===',' && !inQ) { cols.push(cur.trim()); cur=''; }
      else cur+=c;
    }
    cols.push(cur.trim()); return cols;
  };
  const header=splitCSV(lines[0]).map(h=>h.toLowerCase());
  const fIdx=header.indexOf('fronttext')>=0?header.indexOf('fronttext'):header.indexOf('en');
  const bIdx=header.indexOf('backtext')>=0?header.indexOf('backtext'):header.indexOf('ja');
  const cIdx=header.indexOf('count');
  if (fIdx<0||bIdx<0) { toast('列名が見つかりません (FrontText/BackText または en/ja)'); return []; }
  return lines.slice(1).filter(l=>l.trim()).map(line=>{
    const cols=splitCSV(line);
    return { front:cols[fIdx]||'', back:cols[bIdx]||'', count:cIdx>=0?parseInt(cols[cIdx])||0:0 };
  }).filter(w=>w.front&&w.back);
}

// --- Tabs ---
function switchTab(name) {
  const names=['flash','list','add','io'];
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',names[i]===name));
  document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.id===`panel-${name}`));
}

// --- Toast ---
let toastTimer;
function toast(msg) {
  const el=document.getElementById('toast');
  el.textContent=msg; el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>el.classList.remove('show'),2500);
}

loadWords().then(()=>buildDeck());
</script>
</body>
</html>"""

# ---- API ----

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/words", methods=["GET"])
def get_words():
    return jsonify(load_words())

@app.route("/api/words", methods=["POST"])
def add_word():
    words = load_words()
    data = request.json
    new_id = max((w["id"] for w in words), default=0) + 1
    word = {"id": new_id, "front": data["front"], "back": data["back"], "count": 0}
    words.append(word)
    save_words(words)
    return jsonify(word)

@app.route("/api/words/<int:wid>", methods=["PUT"])
def update_word(wid):
    words = load_words()
    data = request.json
    for w in words:
        if w["id"] == wid:
            w["front"] = data.get("front", w["front"])
            w["back"] = data.get("back", w["back"])
            save_words(words)
            return jsonify(w)
    return jsonify({"error": "not found"}), 404

@app.route("/api/words/<int:wid>", methods=["DELETE"])
def delete_word(wid):
    words = [w for w in load_words() if w["id"] != wid]
    save_words(words)
    return jsonify({"ok": True})

@app.route("/api/words/<int:wid>/increment", methods=["POST"])
def increment_count(wid):
    words = load_words()
    for w in words:
        if w["id"] == wid:
            w["count"] += 1
            save_words(words)
            return jsonify(w)
    return jsonify({"error": "not found"}), 404

@app.route("/api/words/reset_counts", methods=["POST"])
def reset_counts():
    words = load_words()
    for w in words:
        w["count"] = 0
    save_words(words)
    return jsonify({"ok": True})

@app.route("/api/words/import", methods=["POST"])
def import_words():
    data = request.json
    incoming = data.get("words", [])
    mode = data.get("mode", "merge")
    words = load_words() if mode == "merge" else []
    existing = {w["front"] for w in words}
    max_id = max((w["id"] for w in words), default=0)
    added = skipped = 0
    for item in incoming:
        front = item.get("front", "")
        back = item.get("back", "")
        count = int(item.get("count", 0))
        if not front or not back:
            continue
        if mode == "merge" and front in existing:
            skipped += 1
            continue
        max_id += 1
        words.append({"id": max_id, "front": front, "back": back, "count": count})
        existing.add(front)
        added += 1
    save_words(words)
    return jsonify({"words": words, "added": added, "skipped": skipped})

if __name__ == "__main__":
    import webbrowser, threading
    print("\n" + "="*45)
    print("  単語帳アプリ 起動中...")
    print("  ブラウザで開く: http://localhost:3000")
    print("  終了: Ctrl+C")
    print("="*45 + "\n")
    threading.Timer(1.0, lambda: webbrowser.open("http://localhost:3000")).start()
    app.run(debug=False, port=3000)

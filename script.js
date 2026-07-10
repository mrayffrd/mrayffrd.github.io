let totals = { genshin: 0, hsr: 0 };
const WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbxL3kVn_10-yypGSc8wnH9QzRxOZ2c_gXEmf2HzOV6-hOgcTaLzD-PSlVTFn3EHzYc3/exec';
let currentGame = '';

const API = "https://script.googleusercontent.com/macros/echo?user_content_key=AUkAhnQWao3zXn-DIANjQAVy3ESqCYjZz4IRN_rk_F2-rznwVkAzdGALoBUXNW6ZJ9YtMiiIFvQcVIRPeJFSg54NN6o7GRu0zV_Bslij3qz3P5OtCItZXLNb9dVAzLOO8wE5mmrl4rQo-qWeLJsw5RV3ioxJgMDe9yBol1sxyqFPuTHyqHVqh62l0a-StuzsdNWrwjSxOk5ZG-YwlS0AA374W2yEa5eokmoEtp-8x79s0u2wuHxn43aBclGPFlkOXIi8SHUKAXftIw8tt6Ruv--kt3gvXWZEpAPind5eCghjM7ecg3HUB8k&lib=M1Wi_wTh7A3YLBi-HiQnFpVLQHf-4KJyd";
async function loadProducts() {
    const res = await fetch(API); // ini langsung baca dari sheet
    const products = await res.json();

    // Kosongin card lama biar ga double
    document.querySelectorAll('.region-card').forEach(card => {
        if(!card.querySelector('.region-title')) card.innerHTML = '';
    });

    products.forEach(p => {
        const targetCard = document.querySelector(`#${p.game}Page.region-card[data-cat="${p.kategori}"]`);
        if(!targetCard) return;
        targetCard.insertAdjacentHTML('beforeend', `
            <div class="area-item">
                <img src="${p.gambar}" onerror="this.src='https://via.placeholder.com/50'" style="width:50px; height:50px; border-radius:8px;">
                <label><input type="checkbox" data-name="${p.nama}" data-price="${p.harga}"><b>${p.nama}</b><br><small>${p.deskripsi}</small></label>
                <span class="price">Rp ${parseInt(p.harga).toLocaleString('id-ID')}</span>
            </div>
        `);
    });
    // aktifin lagi checkbox
    document.querySelectorAll('.area-item input').forEach(cb => {
        cb.addEventListener('change', (e) => { updateTotal(e.target.closest('main').id.replace('Page', '')); })
    });
}
document.addEventListener('DOMContentLoaded', loadProducts);

// ===== TOAST =====
function showToast(message) {
    const toast = document.getElementById('toast');
    if(!toast) return alert(message);
    toast.innerHTML = message;
    toast.classList.add('show');
    setTimeout(() => { toast.classList.remove('show'); }, 4000);
}

// ===== MODAL =====
function closeEnkaModal() { 
    document.getElementById('enkaModal')?.classList.remove('show'); 
}

// ===== TOTAL HARGA =====
function updateTotal(game) {
    let total = 0;
    document.querySelectorAll(`#${game}Page .area-item input:checked`).forEach(i => { total += parseInt(i.dataset.price) });
    totals[game] = total;
    const el = document.getElementById(`totalPrice${game.charAt(0).toUpperCase() + game.slice(1)}`);
    if(el) el.textContent = `Rp ${total.toLocaleString('id-ID')}`;
}

// ===== HISTORI LOKAL =====
function saveOrderToHistory(orderId, gameName) {
    let history = JSON.parse(localStorage.getItem('emu_order_history')) || [];
    if(!history.some(item => item.id === orderId)) {
        history.unshift({ id: orderId, game: gameName, time: new Date().toLocaleDateString('id-ID') });
        localStorage.setItem('emu_order_history', JSON.stringify(history));
    }
}

function loadLocalHistory() {
    const historyListEl = document.getElementById('localHistoryList');
    if(!historyListEl) return;
    let history = JSON.parse(localStorage.getItem('emu_order_history')) || [];
    if(history.length === 0) {
        historyListEl.innerHTML = `<p style="font-size:12px; color:var(--muted); text-align:center;">Belum ada riwayat pesanan di perangkat ini.</p>`;
        return;
    }
    historyListEl.innerHTML = history.map(item => `
        <div class="history-item">
            <div class="history-info" onclick="autoCheckOrder('${item.id}')">
                <div class="history-id">#${item.id}</div>
                <div class="history-game">${item.game} • ${item.time}</div>
            </div>
            <div class="history-actions">
                <button class="history-btn" onclick="autoCheckOrder('${item.id}')">Cek</button>
                <button class="history-btn" style="background:#ff6b6b;" onclick="hapusHistoriPesanan('${item.id}')">Hapus</button>
            </div>
        </div>
    `).join('');
}

function hapusHistoriPesanan(orderId) {
    if(!confirm(`Yakin ingin menghapus pesanan #${orderId}?`)) return;
    let history = JSON.parse(localStorage.getItem('emu_order_history')) || [];
    history = history.filter(item => item.id !== orderId);
    localStorage.setItem('emu_order_history', JSON.stringify(history));
    showToast(`✅ Histori #${orderId} berhasil dihapus.`);
    document.getElementById('hasilCek').innerHTML = '';
    document.getElementById('inputOrderId').value = '';
    loadLocalHistory();
}
function autoCheckOrder(orderId) { document.getElementById('inputOrderId').value = orderId; cekStatus(); }

// ===== BUAT PESAN =====
function generateOrder(game) {
    currentGame = game; 
    let selected = [];
    document.querySelectorAll(`#${game}Page .area-item input:checked`).forEach(i => { 
        selected.push({ name: i.dataset.name, price: parseInt(i.dataset.price) || 0 }); 
    });
    
    if (selected.length === 0) return showToast('⚠️ Pilih minimal 1 layanan');
    const uidVal = document.getElementById(`uid_${game}`).value.trim();
    const nameVal = document.getElementById(`name_${game}`).value.trim(); 
    if(!uidVal || !nameVal) return showToast("⚠️ UID dan NAMA wajib diisi!");
    if(isNaN(uidVal) || (uidVal.length !== 9 && uidVal.length !== 10)) return showToast("⚠️ UID harus 9 atau 10 digit angka");

    const gameTitle = game === 'genshin' ? 'Genshin Impact' : 'Honkai: Star Rail';
    const profileUrl = game === 'genshin' ? `https://akasha.cv/profile/${uidVal}` : `https://enka.network/?hsr&uid=${uidVal}`;
    const siteName = game === 'genshin' ? 'Akasha.cv' : 'Enka.network';

    document.getElementById('enkaModalBody').innerHTML = `
        <p><b>Game:</b> ${gameTitle}</p>
        <p><b>UID:</b> ${uidVal}</p>
        <p><b>Nama:</b> ${nameVal}</p>
        <a href="${profileUrl}" target="_blank" style="color:var(--accent); font-size:12px;">Cek Profile ${siteName} ↗</a>
    `;
    document.getElementById('enkaModal').classList.add('show');
}

// Tombol Lanjutkan di Modal
document.getElementById('modalConfirmBtn')?.addEventListener('click', function() {
    const game = currentGame;
    if(!game) return;
    closeEnkaModal();
    let selected = [];
    document.querySelectorAll(`#${game}Page .area-item input:checked`).forEach(i => { selected.push({ name: i.dataset.name, price: parseInt(i.dataset.price) || 0 }); });
    const uidVal = document.getElementById(`uid_${game}`).value.trim();
    const nameVal = document.getElementById(`name_${game}`).value.trim(); 
    const prefix = game === 'genshin' ? 'GI' : 'HSR';
    const orderId = `${prefix}${Date.now().toString().slice(-6)}`;
    const total = selected.reduce((s, it) => s + it.price, 0);
    const itemsText = selected.map(it => it.name).join(', ');
    const gameNameDisplay = game === 'genshin' ? 'Genshin' : 'HSR';
    const payload = {orderId, game: gameNameDisplay, uid: uidVal, nickname: nameVal, items: itemsText, total: total, wa: nameVal, status: 'Menunggu Pembayaran'};
    
    saveOrderToHistory(orderId, gameNameDisplay);
    fetch(WEB_APP_URL, {method: 'POST', mode: 'no-cors', body: JSON.stringify(payload)});
    
    const waMessage = `Halo Admin EMU Joki 👋\nOrder Baru Masuk!\n\n*ID Pesanan:* #${orderId}\n*Game:* ${payload.game}\n*UID:* ${uidVal}\n*Nama Customer:* ${nameVal}\n\n*Detail Layanan:*\n${selected.map(it => `• ${it.name} - Rp ${it.price.toLocaleString('id-ID')}`).join('\n')}\n\n*Total:* Rp ${total.toLocaleString('id-ID')}`;
    setTimeout(() => { window.open(`https://wa.me/6285150886538?text=${encodeURIComponent(waMessage)}`, '_blank'); }, 500);
    showToast(`✅ Pesanan Berhasil!<br>ID: #${orderId}`);
    document.querySelectorAll(`#${game}Page .area-item input`).forEach(i => i.checked = false);
    document.getElementById(`uid_${game}`).value = "";
    document.getElementById(`name_${game}`).value = "";
    updateTotal(game);
})

function cekStatus() {
    const orderId = document.getElementById('inputOrderId').value.trim();
    if(!orderId) return showToast('⚠️ Masukkan ID Pesanan dulu');
    
    document.getElementById('hasilCek').innerHTML = '⏳ Mencari...';

    fetch(WEB_APP_URL + '?action=cekPesanan&orderId=' + orderId) // TAMBAH action=cekPesanan
        .then(res => {
            if(!res.ok) throw new Error('HTTP ' + res.status);
            return res.json();
        })
        .then(data => {
            if(data.status === 'TIDAK_DITEMUKAN' || !data.orderId) { 
                document.getElementById('hasilCek').innerHTML = `<p style="color:red;">❌ ID Pesanan tidak ditemukan</p>`; 
            } else { 
                let tombolAksiHtml = '';
                if (data.status === 'Menunggu Pembayaran') { 
                    tombolAksiHtml = `<button onclick="batalkanPesanan('${data.orderId}')" class="btn-danger" style="width:100%; margin-top:12px;">❌ Batalkan Pesanan</button>`; 
                } else {
                    const linkWa = `https://wa.me/6285150886538?text=${encodeURIComponent(`Halo Emu, saya mau tanya status pesanan #${data.orderId}`)}`;
                    tombolAksiHtml = `<a href="${linkWa}" target="_blank" style="text-decoration:none;"><button class="btn-primary" style="width:100%; margin-top:12px;">💬 Hubungi Penjual</button></a>`;
                }
                let statusColor = data.status === 'Dibatalkan' ? '#ff6b6b' : data.status === 'Menunggu Pembayaran' ? '#ffa94d' : '#25D366';
                document.getElementById('hasilCek').innerHTML = `
                    <div style="padding:15px; border-radius:8px; border:1px solid var(--border); text-align:left;">
                        <p><b>ID Pesanan:</b> ${data.orderId}</p>
                        <p><b>Game:</b> ${data.game}</p>
                        <p><b>Item:</b> ${data.items}</p>
                        <p><b>Total:</b> Rp ${data.total ? parseInt(data.total).toLocaleString('id-ID') : '0'}</p>
                        <p><b>Status:</b> <span style="color:${statusColor}; font-weight:700;">${data.status}</span></p>
                        ${tombolAksiHtml}
                    </div>
                `; 
                saveOrderToHistory(data.orderId, data.game); // auto simpan ke histori
            }
        }).catch(err => { 
            console.error(err);
            document.getElementById('hasilCek').innerHTML = `<p style="color:red;">❌ Error koneksi ke server. Cek URL Apps Script</p>`; 
        });
}
function batalkanPesanan(orderId) {
    if(!confirm(`Yakin mau membatalkan pesanan #${orderId}?`)) return;
    document.getElementById('hasilCek').innerHTML = '⏳ Memproses pembatalan...';
    showToast('⏳ Memproses pembatalan...');
    fetch(WEB_APP_URL + `?action=cancel&orderId=${orderId}`)
    .then(res => res.json())
    .then(data => {
        showToast(data.status === "success" ? `✅ Pesanan dibatalkan!` : `❌ Gagal membatalkan.`);
        cekStatus();
    }).catch(err => { showToast('❌ Error koneksi'); cekStatus(); });
}

// ===== FILTER & SEARCH =====
function filterCat(el, game) { 
    document.querySelectorAll(`#${game}Page .tab`).forEach(t => t.classList.remove('active')); 
    el.classList.add('active'); 
    applyFilter(game);
}
function searchService(game) { applyFilter(game); }
function applyFilter(game) {
    const searchTerm = document.getElementById(`searchBar${game.charAt(0).toUpperCase() + game.slice(1)}`).value.toLowerCase();
    const activeCat = document.querySelector(`#${game}Page .tab.active`)?.dataset.cat;
    let found = false;
    document.querySelectorAll(`#${game}Page .region-card`).forEach(card => {
        const cardCat = card.dataset.cat;
        const matchCat = !activeCat || cardCat === activeCat;
        const matchSearch = card.innerText.toLowerCase().includes(searchTerm);
        card.style.display = (matchCat && matchSearch) ? 'block' : 'none';
        if (matchCat && matchSearch) found = true;
    });
    document.getElementById(`noResult${game.charAt(0).toUpperCase() + game.slice(1)}`).style.display = found ? 'none' : 'block';
}

// ===== TEMA & INIT =====
function toggleTheme() { 
    const html = document.documentElement; 
    const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; 
    html.setAttribute('data-theme', newTheme); 
    const themeBtn = document.querySelector('.header-actions .icon-btn:last-child'); 
    if(themeBtn) themeBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙'; 
    localStorage.setItem('theme', newTheme); 
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeBtn = document.querySelector('.header-actions .icon-btn:last-child');
    if(themeBtn) themeBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    document.querySelectorAll('.area-item input').forEach(cb => { 
        cb.addEventListener('change', (e) => { 
            const game = e.target.closest('main').id.replace('Page', ''); 
            updateTotal(game); 
        }) 
    });
    const page = document.querySelector('main')?.id;
    if(page === 'genshinPage') applyFilter('genshin');
    if(page === 'hsrPage') applyFilter('hsr');
    if(page === 'cekPage') loadLocalHistory();


function openModal(p){
    document.getElementById('modalImg').src = p.gambar || 'https://via.placeholder.com/300';
    document.getElementById('modalTitle').innerText = p.nama;
    document.getElementById('modalPrice').innerText = `Rp ${parseInt(p.harga).toLocaleString('id-ID')}`;
    document.getElementById('modalDesc').innerText = p.deskripsi || 'Deskripsi belum tersedia.';
    
    document.getElementById('modalAddCart').onclick = () => { addToCart(p); closeModal(); };
    document.getElementById('modalBuy').onclick = () => { buyNow(p); closeModal(); };
    
    document.getElementById('productModal').style.display = 'flex';
}

function closeModal(e){
    if(!e || e.target.id === 'productModal' || e.target.classList.contains('close')){
        document.getElementById('productModal').style.display = 'none';
    }
} 
});
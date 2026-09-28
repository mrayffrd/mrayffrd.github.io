/* =====================================================
   SCRIPT.JS
   ===================================================== */

const API_URL = "https://script.google.com/macros/s/AKfycbz7gHt-Pc5dRyKYwejO7VpMH_nmBR8Cxsk1pVt3y4h9rcXx4KtgF2vBqkOQ4ENz10MJkQ/exec";
// ↑ Pastikan ini URL Web App kamu yang benar

const SECRET = "popit_secret_2026";

// ========== HARGA JUAL (GANTI DI SINI SAJA) ==========
const SELL_PRICE = {
  banner: 5,          // Harga jual 1 banner (Mora)
  petMultiplier: 1    // Harga pet = earnAmount × angka ini
};

let currentUser = null;

async function apiCall(action, data = {}) {
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify({ action, secret: SECRET, ...data })
    });
    return await res.json();
  } catch (err) {
    console.error("API Error:", err);
    return { success: false, message: "Gagal terhubung ke server" };
  }
}

async function login(username, password) {
  const res = await apiCall("login", { username, password });
  if (res.success) {
    currentUser = res.user;
    localStorage.setItem("popit_session", JSON.stringify({ username }));
  }
  return res;
}

async function register(username, password) {
  const res = await apiCall("register", { username, password });
  if (res.success) {
    currentUser = res.user;
    localStorage.setItem("popit_session", JSON.stringify({ username }));
  }
  return res;
}

async function loadSession() {
  const session = localStorage.getItem("popit_session");
  if (!session) return false;
  try {
    const { username } = JSON.parse(session);
    const res = await apiCall("getUser", { username });
    if (res.success) {
      currentUser = res.user;
      return true;
    }
  } catch (e) {}
  return false;
}

function logout() {
  localStorage.removeItem("popit_session");
  currentUser = null;
  window.location.href = "login.html";
}

async function updateUser(updates) {
  if (!currentUser) return { success: false };
  const res = await apiCall("updateUser", {
    username: currentUser.username,
    updates
  });
  if (res.success) currentUser = res.user;
  return res;
}

function updateCurrencyDisplay() {
  if (!currentUser) return;
  document.querySelectorAll(".mora-count").forEach(el => el.textContent = currentUser.mora || 0);
  document.querySelectorAll(".credit-count").forEach(el => el.textContent = currentUser.credit || 0);
}

async function addCurrency(type, amount) {
  if (!currentUser) return;
  const updates = {};
  if (type === "mora") updates.mora = (currentUser.mora || 0) + amount;
  if (type === "credit") updates.credit = (currentUser.credit || 0) + amount;
  await updateUser(updates);
  updateCurrencyDisplay();
}

async function redeemCode(code) {
  if (!currentUser) return { success: false, message: "Belum login" };
  const res = await apiCall("redeem", {
    username: currentUser.username,
    code: code.trim().toUpperCase()
  });
  if (res.success) {
    currentUser = res.user;
    updateCurrencyDisplay();
  }
  return res;
}

async function getGachaConfig(type) {
  return await apiCall("getGacha", { type });
}

async function doGacha(type, times = 1) {
  if (!currentUser) return { success: false, message: "Belum login" };
  const res = await apiCall("doGacha", {
    username: currentUser.username,
    type,
    times
  });
  if (res.success) {
    currentUser = res.user;
    updateCurrencyDisplay();
  }
  return res;
}

async function claimPetEarnings() {
  if (!currentUser) return;
  const res = await apiCall("claimPets", { username: currentUser.username });
  if (res.success && (res.earnedMora > 0 || res.earnedCredit > 0)) {
    currentUser = res.user;
    updateCurrencyDisplay();
    showToast(`🐾 Pet menghasilkan: ${res.earnedMora} Mora & ${res.earnedCredit} Credit!`);
  }
}

async function getChats() {
  const res = await apiCall("getChats");
  return res.chats || [];
}

async function sendChat(message) {
  if (!currentUser || !message.trim()) return;
  return await apiCall("sendChat", {
    username: currentUser.username,
    message: message.trim()
  });
}

function showToast(msg) {
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2300);
}

async function requireLogin() {
  const ok = await loadSession();
  if (!ok) {
    window.location.href = "login.html";
    return false;
  }
  updateCurrencyDisplay();
  claimPetEarnings();
  return true;
}

function timeAgo(ts) {
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  if (m < 1) return "baru saja";
  if (m < 60) return m + " mnt lalu";
  return Math.floor(m / 60) + " jam lalu";
}
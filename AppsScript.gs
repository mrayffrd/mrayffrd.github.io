/*******************************************************
 * GOOGLE APPS SCRIPT - Backend untuk Pop It Game
 * 
 * Cara pakai:
 * 1. Buka Google Spreadsheet yang sudah dibuat
 * 2. Extensions → Apps Script
 * 3. Hapus semua kode default, paste SEMUA kode ini
 * 4. Simpan (Ctrl+S)
 * 5. Deploy → New deployment → Type: Web app
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 6. Copy URL yang muncul, tempel di script.js (API_URL)
 *******************************************************/

const SECRET = "popit_secret_2026"; // HARUS SAMA dengan di script.js
const SS = SpreadsheetApp.getActiveSpreadsheet();

// Nama sheet
const SHEET_USERS = "Users";
const SHEET_REDEEM = "Redeem";
const SHEET_GACHA_ZERO = "GachaZero";
const SHEET_GACHA_INFINITE = "GachaInfinite";
const SHEET_CHAT = "Chat";

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    // Cek secret
    if (data.secret !== SECRET) {
      return respond({ success: false, message: "Unauthorized" });
    }

    const action = data.action;

    switch (action) {
      case "register": return register(data);
      case "login": return login(data);
      case "getUser": return getUser(data);
      case "updateUser": return updateUser(data);
      case "redeem": return redeem(data);
      case "getGacha": return getGacha(data);
      case "doGacha": return doGacha(data);
      case "claimPets": return claimPets(data);
      case "getChats": return getChats();
      case "sendChat": return sendChat(data);
      default:
        return respond({ success: false, message: "Action tidak dikenal" });
    }
  } catch (err) {
    return respond({ success: false, message: "Error: " + err.message });
  }
}

function doGet(e) {
  return respond({ success: true, message: "Pop It API is running" });
}

function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ========== USERS ========== */
function getUsersSheet() {
  let sheet = SS.getSheetByName(SHEET_USERS);
  if (!sheet) {
    sheet = SS.insertSheet(SHEET_USERS);
    sheet.appendRow(["username", "password", "mora", "credit", "data", "lastLogin"]);
  }
  return sheet;
}

function findUserRow(username) {
  const sheet = getUsersSheet();
  const data = sheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]).toLowerCase() === String(username).toLowerCase()) {
      return i + 1; // 1-based
    }
  }
  return -1;
}

function parseUser(row) {
  let extra = {};
  try {
    extra = JSON.parse(row[4] || "{}");
  } catch (e) {}
  return {
    username: row[0],
    mora: Number(row[2]) || 0,
    credit: Number(row[3]) || 0,
    giftBoxes: extra.giftBoxes || [],
    banners: extra.banners || [],
    pets: extra.pets || [],
    activeBanner: extra.activeBanner || null,
    profilePic: extra.profilePic || null,
    lastLogin: row[5] || null
  };
}

function register(data) {
  const { username, password } = data;
  if (!username || !password) {
    return respond({ success: false, message: "Username & password wajib" });
  }
  if (findUserRow(username) !== -1) {
    return respond({ success: false, message: "Username sudah dipakai" });
  }

  const sheet = getUsersSheet();
  const defaultData = JSON.stringify({
    giftBoxes: [],
    banners: [],
    pets: [],
    activeBanner: null,
    profilePic: null
  });
  sheet.appendRow([username, password, 0, 0, defaultData, new Date().toISOString()]);

  const user = {
    username,
    mora: 0,
    credit: 0,
    giftBoxes: [],
    banners: [],
    pets: [],
    activeBanner: null,
    profilePic: null
  };
  return respond({ success: true, user, message: "Berhasil daftar" });
}

function login(data) {
  const { username, password } = data;
  const rowNum = findUserRow(username);
  if (rowNum === -1) {
    return respond({ success: false, message: "Username tidak ditemukan" });
  }
  const sheet = getUsersSheet();
  const row = sheet.getRange(rowNum, 1, 1, 6).getValues()[0];
  if (String(row[1]) !== String(password)) {
    return respond({ success: false, message: "Password salah" });
  }
  // update lastLogin
  sheet.getRange(rowNum, 6).setValue(new Date().toISOString());
  return respond({ success: true, user: parseUser(row) });
}

function getUser(data) {
  const rowNum = findUserRow(data.username);
  if (rowNum === -1) {
    return respond({ success: false, message: "User tidak ditemukan" });
  }
  const sheet = getUsersSheet();
  const row = sheet.getRange(rowNum, 1, 1, 6).getValues()[0];
  return respond({ success: true, user: parseUser(row) });
}

function updateUser(data) {
  const { username, updates } = data;
  const rowNum = findUserRow(username);
  if (rowNum === -1) {
    return respond({ success: false, message: "User tidak ditemukan" });
  }
  const sheet = getUsersSheet();
  const row = sheet.getRange(rowNum, 1, 1, 6).getValues()[0];
  let user = parseUser(row);

  // Apply updates
  if (updates.mora !== undefined) user.mora = Number(updates.mora);
  if (updates.credit !== undefined) user.credit = Number(updates.credit);
  if (updates.giftBoxes !== undefined) user.giftBoxes = updates.giftBoxes;
  if (updates.banners !== undefined) user.banners = updates.banners;
  if (updates.pets !== undefined) user.pets = updates.pets;
  if (updates.activeBanner !== undefined) user.activeBanner = updates.activeBanner;
  if (updates.profilePic !== undefined) user.profilePic = updates.profilePic;

  // Save back
  const extra = JSON.stringify({
    giftBoxes: user.giftBoxes,
    banners: user.banners,
    pets: user.pets,
    activeBanner: user.activeBanner,
    profilePic: user.profilePic
  });
  sheet.getRange(rowNum, 3).setValue(user.mora);
  sheet.getRange(rowNum, 4).setValue(user.credit);
  sheet.getRange(rowNum, 5).setValue(extra);

  return respond({ success: true, user });
}

/* ========== REDEEM ========== */
function getRedeemSheet() {
  let sheet = SS.getSheetByName(SHEET_REDEEM);
  if (!sheet) {
    sheet = SS.insertSheet(SHEET_REDEEM);
    sheet.appendRow(["code", "giftName", "mora", "credit", "maxUses", "usedCount"]);
    // Contoh data
    sheet.appendRow(["WELCOME100", "Welcome Box", 100, 50, 999, 0]);
    sheet.appendRow(["GIFT500", "Big Gift", 500, 0, 50, 0]);
  }
  return sheet;
}

function redeem(data) {
  const { username, code } = data;
  const rowNum = findUserRow(username);
  if (rowNum === -1) return respond({ success: false, message: "User tidak ditemukan" });

  const redeemSheet = getRedeemSheet();
  const dataRange = redeemSheet.getDataRange().getValues();
  let found = null;
  let foundRow = -1;

  for (let i = 1; i < dataRange.length; i++) {
    if (String(dataRange[i][0]).toUpperCase() === String(code).toUpperCase()) {
      found = dataRange[i];
      foundRow = i + 1;
      break;
    }
  }

  if (!found) {
    return respond({ success: false, message: "Kode tidak valid" });
  }

  const maxUses = Number(found[4]) || 1;
  const usedCount = Number(found[5]) || 0;
  if (usedCount >= maxUses) {
    return respond({ success: false, message: "Kode sudah habis dipakai" });
  }

  // Tambah gift box ke user
  const sheet = getUsersSheet();
  const userRow = sheet.getRange(rowNum, 1, 1, 6).getValues()[0];
  let user = parseUser(userRow);

  const gift = {
    name: found[1] || "Gift Box",
    mora: Number(found[2]) || 0,
    credit: Number(found[3]) || 0
  };
  user.giftBoxes = user.giftBoxes || [];
  user.giftBoxes.push(gift);

  // Simpan user
  const extra = JSON.stringify({
    giftBoxes: user.giftBoxes,
    banners: user.banners,
    pets: user.pets,
    activeBanner: user.activeBanner,
    profilePic: user.profilePic
  });
  sheet.getRange(rowNum, 5).setValue(extra);

  // Update usedCount
  redeemSheet.getRange(foundRow, 6).setValue(usedCount + 1);

  return respond({
    success: true,
    user,
    message: `Berhasil! Dapat Gift Box: ${gift.name} (+${gift.mora} Mora, +${gift.credit} Credit saat dibuka)`
  });
}

/* ========== GACHA ========== */
function getGachaSheet(type) {
  const name = type === "zero" ? SHEET_GACHA_ZERO : SHEET_GACHA_INFINITE;
  let sheet = SS.getSheetByName(name);
  if (!sheet) {
    sheet = SS.insertSheet(name);
    // Header: id, name, type, imageUrl, chance, amount, earnType, earnAmount, intervalMinutes
    sheet.appendRow(["id", "name", "type", "imageUrl", "chance", "amount", "earnType", "earnAmount", "intervalMinutes"]);
    
    // Contoh data Zero Gacha
    if (type === "zero") {
      sheet.appendRow(["z1", "Credit Kecil", "credit", "", 40, 20, "", "", ""]);
      sheet.appendRow(["z2", "Mora Kecil", "mora", "", 30, 15, "", "", ""]);
      sheet.appendRow(["z3", "Banner Neon", "banner", "https://picsum.photos/id/1015/800/400", 15, 1, "", "", ""]);
      sheet.appendRow(["z4", "Pet Slime", "pet", "https://picsum.photos/id/237/200", 10, 1, "credit", 5, 30]);
      sheet.appendRow(["z5", "Banner Dark", "banner", "https://picsum.photos/id/1016/800/400", 5, 1, "", "", ""]);
    } else {
      // Infinite
      sheet.appendRow(["i1", "Mora Sedang", "mora", "", 35, 50, "", "", ""]);
      sheet.appendRow(["i2", "Credit Sedang", "credit", "", 30, 40, "", "", ""]);
      sheet.appendRow(["i3", "Banner Galaxy", "banner", "https://picsum.photos/id/1040/800/400", 15, 1, "", "", ""]);
      sheet.appendRow(["i4", "Pet Dragon", "pet", "https://picsum.photos/id/1025/200", 12, 1, "mora", 10, 60]);
      sheet.appendRow(["i5", "Banner Epic", "banner", "https://picsum.photos/id/1036/800/400", 8, 1, "", "", ""]);
    }
  }
  return sheet;
}

function getGacha(data) {
  const sheet = getGachaSheet(data.type);
  const rows = sheet.getDataRange().getValues();
  const items = [];
  for (let i = 1; i < rows.length; i++) {
    items.push({
      id: rows[i][0],
      name: rows[i][1],
      type: rows[i][2],
      imageUrl: rows[i][3],
      chance: Number(rows[i][4]) || 0,
      amount: Number(rows[i][5]) || 1,
      earnType: rows[i][6] || "",
      earnAmount: Number(rows[i][7]) || 0,
      intervalMinutes: Number(rows[i][8]) || 60
    });
  }
  return respond({ success: true, items });
}

function doGacha(data) {
  const { username, type, times } = data;
  const rowNum = findUserRow(username);
  if (rowNum === -1) return respond({ success: false, message: "User tidak ditemukan" });

  const cost = times === 10 ? 900 : 100;
  const currency = type === "zero" ? "credit" : "mora";

  const sheet = getUsersSheet();
  const userRow = sheet.getRange(rowNum, 1, 1, 6).getValues()[0];
  let user = parseUser(userRow);

  if ((user[currency] || 0) < cost) {
    return respond({ success: false, message: "Mata uang tidak cukup" });
  }

  // Kurangi currency
  user[currency] -= cost;

  // Ambil item gacha
  const gachaSheet = getGachaSheet(type);
  const rows = gachaSheet.getDataRange().getValues();
  const pool = [];
  for (let i = 1; i < rows.length; i++) {
    const chance = Number(rows[i][4]) || 0;
    for (let c = 0; c < chance; c++) {
      pool.push({
        id: rows[i][0],
        name: rows[i][1],
        type: rows[i][2],
        imageUrl: rows[i][3],
        amount: Number(rows[i][5]) || 1,
        earnType: rows[i][6] || "",
        earnAmount: Number(rows[i][7]) || 0,
        intervalMinutes: Number(rows[i][8]) || 60
      });
    }
  }

  if (pool.length === 0) {
    return respond({ success: false, message: "Gacha pool kosong" });
  }

  const results = [];
  for (let t = 0; t < times; t++) {
    const item = pool[Math.floor(Math.random() * pool.length)];
    results.push(item);

    if (item.type === "mora") {
      user.mora += item.amount;
    } else if (item.type === "credit") {
      user.credit += item.amount;
    } else if (item.type === "banner") {
      user.banners = user.banners || [];
      // Cegah duplikat id
      if (!user.banners.find(b => b.id === item.id)) {
        user.banners.push({
          id: item.id,
          name: item.name,
          imageUrl: item.imageUrl
        });
      }
    } else if (item.type === "pet") {
      user.pets = user.pets || [];
      if (!user.pets.find(p => p.id === item.id)) {
        user.pets.push({
          id: item.id,
          name: item.name,
          imageUrl: item.imageUrl,
          earnType: item.earnType || "mora",
          earnAmount: item.earnAmount || 5,
          intervalMinutes: item.intervalMinutes || 60,
          lastClaim: new Date().toISOString()
        });
      }
    }
  }

  // Simpan
  const extra = JSON.stringify({
    giftBoxes: user.giftBoxes,
    banners: user.banners,
    pets: user.pets,
    activeBanner: user.activeBanner,
    profilePic: user.profilePic
  });
  sheet.getRange(rowNum, 3).setValue(user.mora);
  sheet.getRange(rowNum, 4).setValue(user.credit);
  sheet.getRange(rowNum, 5).setValue(extra);

  return respond({ success: true, user, results });
}

/* ========== PET CLAIM ========== */
function claimPets(data) {
  const rowNum = findUserRow(data.username);
  if (rowNum === -1) return respond({ success: false, message: "User tidak ditemukan" });

  const sheet = getUsersSheet();
  const userRow = sheet.getRange(rowNum, 1, 1, 6).getValues()[0];
  let user = parseUser(userRow);

  let earnedMora = 0;
  let earnedCredit = 0;
  const now = new Date();

  (user.pets || []).forEach(pet => {
    const last = pet.lastClaim ? new Date(pet.lastClaim) : now;
    const intervalMs = (pet.intervalMinutes || 60) * 60 * 1000;
    const elapsed = now.getTime() - last.getTime();
    const times = Math.floor(elapsed / intervalMs);

    if (times > 0) {
      if (pet.earnType === "mora") {
        earnedMora += times * (pet.earnAmount || 0);
      } else {
        earnedCredit += times * (pet.earnAmount || 0);
      }
      // Update lastClaim (sisa waktu)
      pet.lastClaim = new Date(now.getTime() - (elapsed % intervalMs)).toISOString();
    }
  });

  user.mora += earnedMora;
  user.credit += earnedCredit;

  const extra = JSON.stringify({
    giftBoxes: user.giftBoxes,
    banners: user.banners,
    pets: user.pets,
    activeBanner: user.activeBanner,
    profilePic: user.profilePic
  });
  sheet.getRange(rowNum, 3).setValue(user.mora);
  sheet.getRange(rowNum, 4).setValue(user.credit);
  sheet.getRange(rowNum, 5).setValue(extra);

  return respond({
    success: true,
    user,
    earnedMora,
    earnedCredit
  });
}

/* ========== CHAT ========== */
function getChatSheet() {
  let sheet = SS.getSheetByName(SHEET_CHAT);
  if (!sheet) {
    sheet = SS.insertSheet(SHEET_CHAT);
    sheet.appendRow(["username", "message", "time"]);
  }
  return sheet;
}

function getChats() {
  const sheet = getChatSheet();
  const data = sheet.getDataRange().getValues();
  const threeHours = 3 * 60 * 60 * 1000;
  const now = Date.now();
  const chats = [];

  // Hapus yang sudah lebih dari 3 jam (dari belakang)
  for (let i = data.length - 1; i >= 1; i--) {
    const t = new Date(data[i][2]).getTime();
    if (now - t > threeHours) {
      sheet.deleteRow(i + 1);
    } else {
      chats.unshift({
        username: data[i][0],
        message: data[i][1],
        time: t
      });
    }
  }

  // Batasi 50 pesan terakhir
  return respond({ success: true, chats: chats.slice(-50) });
}

function sendChat(data) {
  const { username, message } = data;
  if (!message || message.length > 200) {
    return respond({ success: false, message: "Pesan tidak valid" });
  }
  const sheet = getChatSheet();
  sheet.appendRow([username, message, new Date().toISOString()]);
  return respond({ success: true });
}

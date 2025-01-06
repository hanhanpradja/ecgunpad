self.addEventListener('install', (event) => {
    console.log('Service Worker diinstal.');
    self.skipWaiting(); // Agar langsung aktif
});

self.addEventListener('activate', (event) => {
    console.log('Service Worker diaktifkan.');
});

// Inisialisasi WebSocket Pusher
const Pusher = require('pusher-js'); // Gunakan pusher-js di dalam service worker
const pusher = new Pusher('7d3db4cc20408e453e6f', {
    cluster: 'ap1',
    forceTLS: true,
    encrypted: true,
});

const channel = pusher.subscribe('ecg-comm-unpad');

// Dengarkan event real-time dan teruskan ke halaman
channel.bind('new-ekg-data', (data) => {
    console.log('Data diterima di Service Worker:', data);

    // Kirim data ke semua client yang aktif (tab atau window browser)
    self.clients.matchAll().then((clients) => {
        clients.forEach((client) => {
            client.postMessage({
                type: 'update-ekg-data',
                data: data,
            });
        });
    });
});

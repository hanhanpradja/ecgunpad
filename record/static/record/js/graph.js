const urlParams = new URLSearchParams(window.location.search);
const idRekaman = urlParams.get('id_rekaman');

async function getSignalData(){
    const response = await fetch(`/record/patient-record/detail/api/sinyalData/?id_rekaman=${idRekaman}`)
    if (response.ok) {
        const data = await response.json();
        return data;
    } else {
        console.error("Error fetching Signal from server");
        return [];
    }
}


(async () => {
    // Dapatkan elemen canvas untuk 3 grafik
    const ctx1 = document.getElementById('dummyGraph');
    const ctx2 = document.getElementById('dummyGraph1');
    const ctx3 = document.getElementById('dummyGraph2');

    if (!ctx1 || !ctx2 || !ctx3) {
        console.error('Canvas elements not found in DOM');
        return;
    }

    // Get context untuk grafik
    const context1 = ctx1.getContext('2d');
    const context2 = ctx2.getContext('2d');
    const context3 = ctx3.getContext('2d');

    // Ambil data sinyal
    const signalData = await getSignalData();
    if (signalData.length === 0) {
        console.error('No signal data received');
        return;
    }

    const signal = signalData[0] || { I: [], II: [], V1: [] };

    // Inisialisasi grafik EKG
    const ekgChart1 = new Chart(context1, {
        type: 'line',
        data: {
            labels: signal.I.map((_, index) => index * 1000),
            datasets: [{
                label: 'Sinyal EKG Saluran I',
                data: signal.I,
                borderColor: 'rgba(255, 0, 0, 1)',
                backgroundColor: 'rgba(255, 0, 0, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { beginAtZero: true, 
                    title: { display: true, text: 'Time (ms)' },
                    ticks: {
                        stepSize: 1,  // Langkah antar label sumbu X adalah 1000 ms
                        callback: function(value, index, ticks) {
                            // Menampilkan hanya kelipatan 1000 ms
                            return value;
                        }
                    } },
                y: { beginAtZero: true, title: { display: true, text: 'Amplitude (mV)' }, suggestedMin: -0.5, suggestedMax: 1.5 }
            }
        }
    });

    const ekgChart2 = new Chart(context2, {
        type: 'line',
        data: {
            labels: signal.II.map((_, index) => index * 1000),
            datasets: [{
                label: 'Sinyal EKG Saluran II',
                data: signal.II,
                borderColor: 'rgba(0, 255, 0, 1)',
                backgroundColor: 'rgba(0, 255, 0, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 0
            }]
        },
        options: { 
            responsive: true,
            scales: {
                x: { beginAtZero: true, 
                    title: { display: true, text: 'Time (ms)' },
                    ticks: {
                        stepSize: 1000,  // Langkah antar label sumbu X adalah 1000 ms
                        callback: function(value, index, ticks) {
                            // Menampilkan hanya kelipatan 1000 ms
                            return value;
                        }
                    } },
                y: { beginAtZero: true, title: { display: true, text: 'Amplitude (mV)' }, suggestedMin: -0.5, suggestedMax: 1.5 }
            }
         }
    });

    const ekgChart3 = new Chart(context3, {
        type: 'line',
        data: {
            labels: signal.V1.map((_, index) => index * 1000),
            datasets: [{
                label: 'Sinyal EKG Saluran V1',
                data: signal.V1,
                borderColor: 'rgba(0, 0, 255, 1)',
                backgroundColor: 'rgba(0, 0, 255, 0.1)',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { beginAtZero: true, 
                    title: { display: true, text: 'Time (ms)' },
                    ticks: {
                        stepSize: 1000,  // Langkah antar label sumbu X adalah 1000 ms
                        callback: function(value, index, ticks) {
                            // Menampilkan hanya kelipatan 1000 ms
                            return value;
                        }
                    } },
                y: { beginAtZero: true, title: { display: true, text: 'Amplitude (mV)' }, suggestedMin: -0.5, suggestedMax: 1.5 }
            }
        }
    });
})();

let isRecording = false; // Menyimpan status apakah perekaman sedang berlangsung

async function toggleRecording() {
    const button = document.getElementById("recordButton");

    if (isRecording) {
        // Jika sedang merekam, hentikan perekaman
        await stopRecording();
        // Ubah tombol kembali menjadi "Rekam"
        button.textContent = "Rekam";
        isRecording = !isRecording;
    } else {
        // Jika tidak sedang merekam, mulai perekaman
        await showConfirmationModal();
        // Ubah tombol menjadi "Hentikan"
        
    }

}

function showConfirmationModal() {
    const modal = new bootstrap.Modal(document.getElementById("confirmationModal"));
    modal.show();
}

function showNameInputModal() {
    const confirmationModal = bootstrap.Modal.getInstance(document.getElementById("confirmationModal"));
    confirmationModal.hide();
    
    const modal = new bootstrap.Modal(document.getElementById("nameInputModal"));
    modal.show();
}

function openRegistrationModal() {
    const confirmationModal = bootstrap.Modal.getInstance(document.getElementById("confirmationModal"));
    confirmationModal.hide();

    const registrationModal = new bootstrap.Modal(document.getElementById("formModal"));
    registrationModal.show();
}

// Function to fetch NIKs from Django backend
async function fetchNIKs() {
    const response = await fetch("/api/niks/");
    if (response.ok) {
        const data = await response.json();
        return data;
    } else {
        console.error("Error fetching NIKs from server");
        return [];
    }
}

// Function to filter and show suggestions
async function filterSuggestions() {
    const input = document.getElementById("inputNIK").value.toLowerCase();
    const registeredNIKs = await fetchNIKs();
    
    const suggestions = registeredNIKs.filter((nik) =>
        nik.includes(input)
    );

    const suggestionBox = document.getElementById("suggestionBox");
    suggestionBox.innerHTML = ""; // Clear previous suggestions

    if (input.trim() && suggestions.length > 0) {
        suggestions.forEach((nik) => {
            const item = document.createElement("div");
            item.className = "dropdown-item";
            item.textContent = nik;
            item.onclick = () => selectSuggestion(nik); // Set NIK on click
            suggestionBox.appendChild(item);
        });
        suggestionBox.style.display = "block"; // Show suggestions
    } else {
        suggestionBox.style.display = "none"; // Hide if no matches
    }
}

// Function to handle suggestion click
function selectSuggestion(nik) {
    document.getElementById("inputNIK").value = nik;
    document.getElementById("suggestionBox").style.display = "none";
}

// Show suggestions on input click
function showSuggestions() {
    const input = document.getElementById("inputNIK").value.trim();
    if (input) {
        filterSuggestions();
    }
}


async function submitForm() {
    const name = document.getElementById("name").value;
    const umur = document.getElementById("umur").value;
    const nik = document.getElementById("NIK").value;

    if (name.trim() && umur.trim() && nik.trim()) {
        // Simpan data di sessionStorage untuk digunakan nanti
        sessionStorage.setItem("nama", name);
        sessionStorage.setItem("umur", umur);
        sessionStorage.setItem("nik", nik);

        // Tampilkan modal konfirmasi
        document.getElementById("confirmName").textContent = name;
        document.getElementById("confirmUmur").textContent = umur;
        document.getElementById("confirmNIK").textContent = nik;

        // Tampilkan modal konfirmasi
        const formResultModal = new bootstrap.Modal(document.getElementById("formResultModal"));
        formResultModal.show();
    } else {
        // alert("Mohon isi semua data dengan benar.");
        alert(name);
        alert(umur);
        alert(nik);
    }
}


async function startRecording(event) {
    const buttonId = event.target.id;

    try {
        let pasienId;

        if (buttonId === "startRecording") {
            // Pasien baru: ambil data tambahan
            const name = document.getElementById("name").value;
            const umur = document.getElementById("umur").value;
            const nik = document.getElementById("NIK").value;


            if (!name || !umur || !nik) {
                alert("Mohon lengkapi data untuk pasien baru.");
                return;
            }

            // Simpan data pasien baru ke database
            const response = await fetch("/new-pasien-rekam/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ nama: name, umur, nik })
            });

            // if (!response.ok) throw new Error("Gagal menyimpan data pasien baru.");
            // const result = await response.json();
            const result = await handleFetchResponse(response)
            pasienId = result.id; // Ambil ID pasien dari response
        } else if (buttonId === "continueRecording") {
            // Pasien lama: Periksa NIK dan dapatkan ID pasien
            const inputnik = document.getElementById("inputNIK").value;
        
            if (!inputnik) {
                alert("Mohon isi NIK dengan benar!!");
                return; // Stop execution
            }
        
            try {
                const response = await fetch("/check-nik/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    },
                    body: JSON.stringify({ nik: inputnik }) // Update key to "nik"
                });
        
                // if (!response.ok) throw new Error("NIK tidak ditemukan.");
                // const result = await response.json();
                const result = await handleFetchResponse(response)
                pasienId = result.id; // Ambil ID pasien berdasarkan NIK
            } catch (error) {
                alert(error.message);
            }
            const modalElement = document.getElementById("nameInputModal");
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) modalInstance.hide();
        }
        

        if (!pasienId) {
            throw new Error("ID pasien tidak valid.");
        }

        // Tutup modal konfirmasi jika terbuka
        const modalElement = document.getElementById("formResultModal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) modalInstance.hide();

        // Mulai perekaman
        const recordResponse = await fetch("/test-process-data/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ id_pasien: pasienId })
        });

        // if (!recordResponse.ok) throw new Error("Gagal memulai perekaman.");
        // const recordResult = await recordResponse.json();
        const recordResult = await handleFetchResponse(recordResponse)
        console.log("Proses perekaman dimulai:", recordResult);

        // Perbarui tombol perekaman
        isRecording = !isRecording
        const startButton = document.getElementById('recordButton');
        startButton.textContent = "Hentikan Perekaman";

        // Inisialisasi Pusher untuk menerima data real-time
        initializePusher();

    } catch (error) {
        stopRecording(); // Hentikan perekaman jika terjadi kesalahan
        console.error("Terjadi kesalahan:", error);
        alert("Terjadi kesalahan: " + error.message);
    }
}

// Fungsi untuk menginisialisasi Pusher
function initializePusher() {
    const pusher = new Pusher('7d3db4cc20408e453e6f', {
        cluster: 'ap1',
        forceTLS: true,
        encrypted: true
    });

    // Subscribe ke channel yang sesuai
    const channel = pusher.subscribe('ecg-comm-unpad');

    // Dengarkan event real-time
    channel.bind('new-ekg-data', function (data) {
        console.log("Data real-time diterima:", data);
        updatePatientInfo(data);
        updateAdminInfo(data);
        updateDiagnosis(data);

        // Simpan data di localStorage
        sessionStorage.setItem('realTimeData', JSON.stringify(data));

        const savedData = sessionStorage.getItem('realTimeData');
        if (savedData) {
            const parsedData = JSON.parse(savedData);
            updatePatientInfo(parsedData);
            updateAdminInfo(parsedData);
            updateDiagnosis(parsedData); 
        }
    });
}

// Fungsi untuk memperbarui informasi pasien
function updatePatientInfo(data) {
    document.getElementById('patient-name').textContent = data.nama || '-';
    document.getElementById('recording-time').textContent = new Date(data['record-date']).toLocaleString() || '-';
    document.getElementById('patient-age').textContent = `${data.umur || '-'} y.o`;
}

// Fungsi untuk memperbarui informasi admin
function updateAdminInfo(data) {
    document.getElementById('admin-name').textContent = data.admin || 'Admin 1';
    const deviceStatusElement = document.getElementById('device-status');
    deviceStatusElement.textContent = data.device_status || 'Offline';
    deviceStatusElement.classList.remove('text-success', 'text-danger');
    deviceStatusElement.classList.add(data.device_status === 'Online' ? 'text-success' : 'text-danger');
}

// Fungsi untuk memperbarui diagnosis
function updateDiagnosis(data) {
    const diagnosisElement = document.getElementById('diagnosis-status');
    diagnosisElement.textContent = data.klasifikasi || '-';
    diagnosisElement.classList.remove('text-danger', 'text-success');
    diagnosisElement.classList.add(data.klasifikasi === 'NORMAL' ? 'text-success' : 'text-danger');
}

function stopRecording() {
    // Kirim request ke backend untuk menghentikan perekaman
    fetch('/stop-process/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})  // Bisa ditambahkan data lain jika diperlukan
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);  // Menampilkan respons dari server
        alert(data.message);
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function forcedStop() {
    fetch ('/test-process-data/'), {
        
    }
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function handleFetchResponse(response) {
    if (!response.ok) {
        const errorData = await response.json(); // Parsing JSON error
        const errorMessage = errorData.error || "Terjadi kesalahan pada server.";
        throw new Error(errorMessage);
    }
    return await response.json(); // Jika tidak ada masalah, lanjutkan parsing hasil
}
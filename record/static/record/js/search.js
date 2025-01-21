async function fetchPatient() {
    try {
        const response = await fetch("/record/search/")
        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            console.error("Error fetching patient data")
            return []
        } 
    
    } catch (error) {
        console.error("Fetch error:", error);
        return [];
    }
}

async function suggestionPatient() {
    const input = document.getElementById('searchPatient').value.toLowerCase();
    const allPatient = await fetchPatient();

    const suggestions = allPatient.filter((patient) =>
        patient.nama.toLowerCase().includes(input)
    );

    const suggestionBox = document.getElementById('patientCards');

    // Kosongkan kotak saran sebelumnya
    suggestionBox.innerHTML = "";

    // Tampilkan saran hanya jika input memenuhi kriteria
    if (input.trim() && suggestions.length > 0) {
        suggestions.forEach(patient => {
            // Buat elemen card
            const card = document.createElement('div');
            card.className = 'card';

            // Buat elemen card-body
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body';

            // Buat elemen card-title
            const cardTitle = document.createElement('h5');
            cardTitle.className = 'card-title';
            cardTitle.textContent = patient.nama;

            // Buat elemen card-text untuk NIK
            const cardText = document.createElement('p');
            cardText.className = 'card-text nik';
            cardText.textContent = patient.nik;

            // Buat elemen link
            const link = document.createElement('a');
            link.className = 'btn btn-primary';
            link.href = `/record/patient-record/?id_pasien=${patient.id_pasien}`;
            link.textContent = 'Lihat Detail';

            // Susun elemen-elemen ke dalam card
            cardBody.appendChild(cardTitle);
            cardBody.appendChild(cardText);
            cardBody.appendChild(link);
            card.appendChild(cardBody);

            // Tambahkan card ke kotak saran
            suggestionBox.appendChild(card);
        });

        // Tampilkan kotak saran
        suggestionBox.style.display = 'block';
    } else {
        suggestionBox.style.display = 'none';
    }
}


function showSuggestions() {
    const input = document.getElementById("searchPatient").value.trim();
    if (input) {
        suggestionPatient();
    }
}
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
    
    .catch(error => {
        console.error("Error:", error);
    });
}

window.onload = function () {
    stopRecording();
};
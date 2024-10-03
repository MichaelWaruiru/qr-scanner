function onScanSuccess(decodedText, decodedResult) {
    console.log(`Code matched = ${decodedText}`, decodedResult);

    // Parse the QR code data which contains product information
    let productData = JSON.parse(decodedText);
    
    // Prompt user for their phone number
    let phoneNumber = prompt("Please enter your phone number to complete payment:");

    // Send the product data and phone number to the server for payment initiation
    fetch('/initiate_payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productData.id, phone_number: phoneNumber }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);  // Show success message
        } else if (data.error) {
            alert("Payment initiation failed: " + data.error);  // Show error message
        }
    });
}

var html5QrCode = new Html5Qrcode("qr-reader");
html5QrCode.start({ facingMode: "environment" }, {
    fps: 10,
    qrbox: 250
}, onScanSuccess);

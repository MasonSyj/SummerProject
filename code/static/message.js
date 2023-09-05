function generateInformation(error_message) {
    var current_information = document.getElementById("errors");

    const currentDate = new Date();
    let time = `${currentDate.toLocaleDateString()} ${currentDate.getHours().toString().padStart(2, '0')}:${currentDate.getMinutes().toString().padStart(2, '0')}:${currentDate.getSeconds().toString().padStart(2, '0')}  `
    let new_information = time + error_message + '\n';
    new_information += current_information.value

    current_information.value = new_information;
}


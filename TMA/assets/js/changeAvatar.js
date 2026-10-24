document.addEventListener('DOMContentLoaded', function () {
    const matches = document.getElementsByClassName("avatarButton");

    for (let i = 0; i < matches.length; i++) {

        matches[i].addEventListener('click', function () {
            console.log("Inside");
            const imgSrc = document.getElementById("img" + matches[i].id).src;
            console.log(imgSrc);

            fetch('/chooseAvatar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: imgSrc })
            })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error('Request failed');
                    }
                    return response.json();
                })
                .then(function (data) {
                    console.log(data['path']);
                    console.log('Success!');

                    document.getElementById('userAvatar').src = data['path'];
                })
                .catch(function () {
                    alert("Error");
                });
        });
    };
});
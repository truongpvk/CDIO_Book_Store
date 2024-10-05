function sort() {
    const sortTag = document.getElementById('sort-book');
    var sortValue = sortTag.value;

    if (sortValue) {
        postValue(sortValue);
        localStorage.setItem('bookSort', sortValue);
    }
};

function postValue(sortValue) {
    var msg = {
        'sortValue': sortValue,
    };

    fetch("/sort=" + sortValue, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(msg),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response is not okay!');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        window.location.href = data.redirectURL;
    })
    .catch(error => {
        console.log(error)
    });
};
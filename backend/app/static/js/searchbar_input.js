function search(event) {
    if (event.key === 'Enter') {
        const searchContent = document.getElementById('search-bar').value;
        console.log(searchContent);
        if (searchContent) {
            postContent(searchContent);
        }
    }
};

function postContent(content) {
    var msg = {
        'search_string': content,
    }

    fetch("/search=" + content, {
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
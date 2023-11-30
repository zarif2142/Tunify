// Replace 'YOUR_CLIENT_ID' and 'YOUR_CLIENT_SECRET' with your actual values
const clientId = '298e09f0d6594fa599cff0b1e36f9222';
const clientSecret = 'bf366f460b9e4496a29b6ebdcd495844';
const redirectUri = 'http://localhost:5000/redirect'; // Replace with your actual redirect URI

// Function to exchange the authorization code for tokens (Add your logic here)
async function exchangeAuthorizationCode(authorizationCode) {
    // Spotify token endpoint
    const tokenUrl = 'https://accounts.spotify.com/api/token';

    // Create form data
    const formData = new URLSearchParams();
    formData.append('grant_type', 'authorization_code');
    formData.append('code', authorizationCode);
    formData.append('redirect_uri', redirectUri);

    // Create Basic Authentication header
    const basicAuth = btoa(`${clientId}:${clientSecret}`);

    try {
        // Exchange the authorization code for access and refresh tokens
        const response = await fetch(tokenUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${basicAuth}`,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        const tokenData = await response.json();
        const accessToken = tokenData.access_token;
        const refreshToken = tokenData.refresh_token;

        // Handle the access and refresh tokens as needed
        console.log('Access Token:', accessToken);
        console.log('Refresh Token:', refreshToken);

    } catch (error) {
        console.error('Error exchanging authorization code:', error);
    }
}

// Example function that can be called when the page loads
function onPageLoad() {
    // Extract the authorization code from the URL (Add your logic here)
    const authorizationCode = getAuthorizationCodeFromURL();

    if (authorizationCode) {
        // Call the function to exchange the authorization code for tokens
        exchangeAuthorizationCode(authorizationCode);
    }
}

// Function to extract the authorization code from the URL (Add your logic here)
function getAuthorizationCodeFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('code');
}

// Call the onPageLoad function when the page loads
window.addEventListener('load', onPageLoad);






function onPageLoad() {
    // Extract the authorization code from the URL (Add your logic here)
    const authorizationCode = getAuthorizationCodeFromURL();

    if (authorizationCode) {
        // Call the function to exchange the authorization code for tokens
        exchangeAuthorizationCode(authorizationCode);
    } else {
        // No authorization code, directly fetch song recommendation
        fetchSongRecommendation();
    }
}

// Function to fetch song recommendation
function fetchSongRecommendation() {
    fetch('/get-song-recommendation')
        .then(response => response.json())
        .then(data => {
            const recommendationDiv = document.getElementById('song-recommendation');
            recommendationDiv.innerHTML = ''; // Clear previous recommendations

            if(data.title && data.artist && data.spotify_url) {
                const songLink = document.createElement('a');
                songLink.href = data.spotify_url; // Set the href to the Spotify URL
                songLink.target = '_blank'; // Open in a new tab
                songLink.className = 'spotify-song-button'; // Add styling class if needed
                songLink.textContent = `Listen to ${data.title} by ${data.artist}`;

                recommendationDiv.appendChild(songLink); // Append the anchor element to the recommendation div
            } else {
                recommendationDiv.textContent = 'No recommendation available.';
            }
        })
        .catch(error => {
            console.error('Error fetching song recommendation:', error);
        });
}

// Event listener for the shuffle image button
document.querySelector('.shuffle-button').addEventListener('click', fetchSongRecommendation);

// Call the onPageLoad function when the page loads
window.addEventListener('load', onPageLoad);

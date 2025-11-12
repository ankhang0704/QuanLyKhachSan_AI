// --- HÀM MỞ MODAL ZOOM ---
function openImageModal(imageUrl) {
    const modal = document.getElementById('image_zoom_modal');
    const modalImage = document.getElementById('modal_zoom_image');
    if (modal && modalImage) {
        modalImage.src = imageUrl;
        modal.showModal();
    }
}

// --- HÀM TIỆN ÍCH COOKIE (CHO CSRF) ---
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

// --- HÀM HIỂN THỊ CHATBOT ---
function displayMessage(message, sender) {
    const chatClass = (sender === 'user') ? 'chat-end' : 'chat-start';
    const bubbleClass = (sender === 'user') ? 'chat-bubble-primary' : 'chat-bubble-info';

    const messageHTML = `
        <div class="chat ${chatClass}">
            <div class="chat-bubble ${bubbleClass}">
                ${message}
            </div>
        </div>
        `;
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.insertAdjacentHTML('beforeend', messageHTML);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// --- LOGIC CHÍNH KHI TẢI TRANG ---
document.addEventListener("DOMContentLoaded", function () {

    // 1. Logic cho Back to Top
    const backToTopBtn = document.getElementById('backToTop');
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.remove('opacity-0', 'pointer-events-none');
            } else {
                backToTopBtn.classList.add('opacity-0', 'pointer-events-none');
            }
        });
        backToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 2. Logic cho Active Menu
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.navbar a[href]');
    menuLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === '/' && currentPath === '/') {
            link.classList.add('active');
        } else if (linkPath !== '/' && currentPath.startsWith(linkPath)) {
            link.classList.add('active');
        }
    });

    // 3. Logic cho Theme Toggle (Light/Dark)
    const themeToggle = document.getElementById('theme-toggle');
    const docHtml = document.documentElement;

    function applyTheme(theme) {
        docHtml.setAttribute('data-theme', theme);
        if (themeToggle) {
            themeToggle.checked = (theme === 'dark');
        }
    }
    function toggleTheme() {
        const currentTheme = docHtml.getAttribute('data-theme') || 'light';
        const newTheme = (currentTheme === 'dark') ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // 4. Logic cho Chat Pop-up
    const chatToggleBtn = document.getElementById('chat-toggle-btn');
    const chatPopup = document.getElementById('chat-popup');
    const closeChatBtn = document.getElementById('close-chat-btn');

    if (chatToggleBtn && chatPopup && closeChatBtn) {
        chatToggleBtn.addEventListener('click', () => {
            chatPopup.classList.toggle('hidden');
        });
        closeChatBtn.addEventListener('click', () => {
            chatPopup.classList.add('hidden');
        });
    }

    // 5. LOGIC CHAT FORM SUBMIT (Hoàn nguyên về phiên bản gốc hoạt động của bạn)
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');

    if (chatForm) {
        chatForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Ngăn trang tải lại
            const userMessage = chatInput.value.trim();
            if (userMessage === '') return;

            displayMessage(userMessage, 'user');
            chatInput.value = '';

            fetch('/api/chatbot/', { // Đảm bảo URL này là chính xác
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ question: userMessage })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Lỗi máy chủ: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.answer) {
                        displayMessage(data.answer, 'bot');
                    } else if (data.error) {
                        displayMessage(`Lỗi: ${data.error}`, 'bot');
                    }
                })
                .catch(error => {
                    console.error('Lỗi khi gọi API:', error);
                    displayMessage('Rất tiếc, đã có lỗi xảy ra. Vui lòng thử lại.', 'bot');
                });
        });
    }
    // --- KẾT THÚC LOGIC CHATBOT ---

}); // Hết DOMContentLoaded
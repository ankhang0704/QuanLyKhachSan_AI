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



// --- HÀM LOGIC CHÍNH KHI TẢI TRANG ---
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

    let bestMatch = null;
    let bestMatchLength = 0;

    menuLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (!linkPath || linkPath === '#' || link.closest('.dropdown-content')) {
            return;
        }
        if (linkPath === '/' && currentPath === '/') {
            bestMatch = link;
            bestMatchLength = 1;
            return;
        }
        if (linkPath !== '/' && currentPath.startsWith(linkPath)) {
            if (linkPath.length > bestMatchLength) {
                bestMatch = link;
                bestMatchLength = linkPath.length;
            }
        }
    });

    if (bestMatch) {
        bestMatch.classList.add('active');
        const parentDetails = bestMatch.closest('details');
        if (parentDetails) {
            parentDetails.querySelector('summary').classList.add('active');
        }
    }


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


    // 4. Logic cho Chat Pop-up (Cập nhật để thêm tin nhắn chào mừng)
    const chatPopup = document.getElementById('chat-popup');
    const closeChatBtn = document.getElementById('close-chat-btn');
    const openChatBubble = document.getElementById('open-chat-bubble');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    function openChat() {
        chatPopup.classList.remove('hidden', 'scale-95', 'opacity-0');
        chatPopup.classList.add('scale-100', 'opacity-100');
        openChatBubble.classList.add('scale-0', 'opacity-0');
    }

    function closeChat() {
        chatPopup.classList.add('scale-95', 'opacity-0');
        chatPopup.classList.remove('scale-100', 'opacity-100');
        setTimeout(() => chatPopup.classList.add('hidden'), 300);
        openChatBubble.classList.remove('scale-0', 'opacity-0');
    }

    openChatBubble.addEventListener('click', openChat);
    closeChatBtn.addEventListener('click', closeChat);

    // -- Logic gửi tin nhắn --
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message) {
            displayMessage(message, 'user');
            chatInput.value = '';

            showLoadingIndicator();
            // Quay lại logic trả lời tự động
                fetch('/api/chatbot/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({ question: message })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Lỗi máy chủ: ' + response.status);
                        }
                        return response.json();
                    })
                    .then(data => {
                        // 4. Ẩn loading
                        hideLoadingIndicator();

                        // 5. Hiển thị trả lời
                        if (data.answer) {
                            displayMessage(data.answer, 'bot');
                        } else if (data.error) {
                            displayMessage(`Lỗi: ${data.error}`, 'bot');
                        } else {
                            displayMessage('Rất tiếc, tôi không nhận được phản hồi. Vui lòng thử lại.', 'bot');
                        }
                    })
                    .catch(error => {
                        // 4. Ẩn loading (kể cả khi lỗi)
                        hideLoadingIndicator();

                        // 5. Hiển thị lỗi
                        console.error('Lỗi khi gọi API:', error);
                        displayMessage('Rất tiếc, đã có lỗi xảy ra. Vui lòng thử lại.', 'bot');
                    });
        }
    });
    // --- LOGIC CHATBOT MỚI (HOÀN THIỆN HƠN) ---

    // 1. Hiển thị "..." loading (Dùng component của daisyUI)
    function showLoadingIndicator() {
        if (!chatMessages) return;

        const loadingHTML = `
                <div id="loading-indicator" class="chat chat-start">
                    <div class="chat-image avatar">
                        <!-- CẬP NHẬT: Dùng <img> thay vì icon -->
                        <div class="w-10 rounded-full">
                            <img alt="Bot Avatar" src="https://placehold.co/40x40/A9ADC1/3D4451?text=Bot&font=inter" />
                        </div>
                    </div>
                    <div class="chat-bubble">
                        <!-- Component loading của daisyUI -->
                        <span class="loading loading-dots loading-sm"></span>
                    </div>
                </div>
                `;
        chatMessages.insertAdjacentHTML('beforeend', loadingHTML);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 2. Ẩn "..." loading
    function hideLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // 3. Hàm hiển thị tin nhắn (Cập nhật phong cách Messenger)
    // SỬA LỖI: Logic đã được sửa lại cho đúng
    function displayMessage(message, sender) {
        if (!chatMessages) return;

        let messageHTML = '';

        if (sender === 'user') {
            // 1. Xử lý tin nhắn của user: escape HTML và thay \n bằng <br>
            const formattedMessage = message
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/\n/g, "<br>");

            // KIỂU MESSENGER: Không có avatar, dùng chat-bubble-primary
            messageHTML = `
                    <div class="chat chat-end">
                        <div class="chat-bubble chat-bubble-primary text-white">
                            ${formattedMessage}
                        </div>
                    </div>
                    `;
        } else { // 'bot'
            // 2. Tin nhắn của bot: Xử lý \n bằng <br>
            // (Chúng ta không dùng Gemini nữa nên không cần format markdown)
            const formattedMessage = message.replace(/\n/g, "<br>");

            messageHTML = `
                    <div class="chat chat-start">
                        <div class="chat-image avatar">
                            <!-- CẬP NHẬT: Dùng <img> thay vì icon -->
                            <div class="w-10 rounded-full">
                                <img alt="Bot Avatar" src="https://placehold.co/40x40/A9ADC1/3D4451?text=Bot&font=inter" />
                            </div>
                        </div>
                        <div class="chat-bubble">
                            ${formattedMessage}
                        </div>
                    </div>
                    `;
        }

        chatMessages.insertAdjacentHTML('beforeend', messageHTML);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    // --- KẾT THÚC LOGIC CHATBOT ---

    // 6. Logic cho Datepicker trong các Modal Promo
    const promoModals = document.querySelectorAll('dialog[id^="modal_promo_"]');
    // Logic kiểm soát ngày Check-in và Check-out
    promoModals.forEach(modal => {
        const checkInInput = modal.querySelector('input[name="check_in"]');
        const checkOutInput = modal.querySelector('input[name="check_out"]');

        if (!checkInInput || !checkOutInput) return;

        const today = new Date().toISOString().split('T')[0];

        // 1. Set min cho cả hai là hôm nay
        checkInInput.min = today;
        checkOutInput.min = today;

        // 2. Logic khi người dùng chọn ngày Check-in
        checkInInput.addEventListener('change', () => {
            if (checkInInput.value) {
                const checkInDate = new Date(checkInInput.value);
                // Ngày trả phòng phải sau ngày nhận phòng 1 ngày
                const nextDay = new Date(checkInDate);
                nextDay.setDate(checkInDate.getDate() + 1);

                const nextDayStr = nextDay.toISOString().split('T')[0];

                // Set min cho check-out
                checkOutInput.min = nextDayStr;

                // Nếu check-out hiện tại < min mới, thì reset nó
                if (checkOutInput.value && checkOutInput.value < nextDayStr) {
                    checkOutInput.value = nextDayStr;
                }
            }
        });

        // 3. Logic khi người dùng chọn ngày Check-out (để đảm bảo)
        checkOutInput.addEventListener('change', () => {
            if (checkOutInput.value && checkInInput.value) {
                if (checkOutInput.value <= checkInInput.value) {
                    // Nếu ngày trả phòng = ngày nhận phòng, báo lỗi (hoặc tự sửa)
                    const checkInDate = new Date(checkInInput.value);
                    const nextDay = new Date(checkInDate);
                    nextDay.setDate(checkInDate.getDate() + 1);
                    checkOutInput.value = nextDay.toISOString().split('T')[0];
                }
            }
        });
    });
    // --- 7. LOGIC CHO HOME PAGE FORM DATE PICKER (MỚI) ---
    // Logic này chỉ chạy nếu tìm thấy các ID của form trang chủ
    const homeCheckInInput = document.getElementById('check_in');
    const homeCheckOutInput = document.getElementById('check_out');

    if (homeCheckInInput && homeCheckOutInput) {
        const today = new Date().toISOString().split('T')[0];

        // 1. Set min cho cả hai là hôm nay
        homeCheckInInput.min = today;
        homeCheckOutInput.min = today;

        // 2. Logic khi người dùng chọn ngày Check-in
        homeCheckInInput.addEventListener('change', () => {
            if (homeCheckInInput.value) {
                const checkInDate = new Date(homeCheckInInput.value);
                // Ngày trả phòng phải sau ngày nhận phòng 1 ngày
                const nextDay = new Date(checkInDate);
                nextDay.setDate(checkInDate.getDate() + 1);

                const nextDayStr = nextDay.toISOString().split('T')[0];

                // Set min cho check-out
                homeCheckOutInput.min = nextDayStr;

                // Nếu check-out hiện tại < min mới, thì reset nó
                if (homeCheckOutInput.value && homeCheckOutInput.value < nextDayStr) {
                    homeCheckOutInput.value = nextDayStr;
                }
            }
        });
    }


    // --- HÀM MỞ MODAL ZOOM ---
    // (Giữ lại hàm này vì nó được gọi từ các file template khác)
    window.openImageModal = function (imageUrl) {
        const modal = document.getElementById('image_zoom_modal');
        const modalImage = document.getElementById('modal_zoom_image');
        if (modal && modalImage) {
            modalImage.src = imageUrl;
            modal.showModal();
        }
    }

}); // Hết DOMContentLoaded
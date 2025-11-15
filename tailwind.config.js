/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './templates/**/*.html', // Quét tất cả file HTML trong template
        './**/templates/**/*.html', // Quét tất cả template trong các app
    ],
    safelist: [
        'chat',
        'chat-start',
        'chat-end',
        'chat-top',
        'chat-bubble',
        'chat-bubble-primary',
        'chat-bubble-info',
        'chat-image',
        'avatar',
        'rounded-2xl', // Đây là class bị thiếu khiến vỡ layout
        'shadow-sm', // Đây là class bị thiếu khiến vỡ layout
        'grid',
        'place-items-center',
        'loading-dots',
        'items-start',
        // Thêm bất kỳ class nào bạn tạo bằng JS mà Tailwind không thấy
    ],
    theme: {
        extend: {
            colors: {
                'primary': '#0066CC',
                'primary-light': '#0099FF',
                'primary-dark': '#003D82',
                'accent': '#FF9500',
                'accent-light': '#FFB84D',
                'sand': '#FFF5E6',
                'sand-dark': '#FFE4CC',
            },
            fontFamily: {
                'sans': ['Inter', 'sans-serif'], // Áp dụng font Inter cho toàn trang
            }
        }
    },
    plugins: [
        require("daisyui")
    ],
    daisyui: {
        themes: [
            {
                light: {
                    // Sử dụng màu tùy chỉnh của bạn
                    "primary": "#0066CC",
                    "primary-focus": "#0052a3",
                    "primary-content": "#FFFFFF",
                    "accent": "#FF9500",
                    "accent-content": "#FFFFFF",
                    "base-100": "#FFF5E6", // Sand
                    "base-200": "#FFE4CC", // Sand-dark
                    "base-300": "#FFD9B3",

                    // Giữ lại các màu DaisyUI mặc định khác
                    ...require("daisyui/src/theming/themes")["[data-theme=light]"],
                },
                dark: {
                    // Sử dụng màu tùy chỉnh của bạn
                    "primary": "#007bff",
                    "primary-focus": "#0099FF",
                    "primary-content": "#FFFFFF",
                    "accent": "#FF9500",
                    "accent-content": "#FFFFFF",

                    // Giữ lại các màu DaisyUI mặc định khác
                    ...require("daisyui/src/theming/themes")["[data-theme=dark]"],
                    "base-100": "#2a303c",
                    "base-200": "#1d232a",
                    "base-300": "#15191e",
                },
            },
        ],
    },
}
document.addEventListener('DOMContentLoaded', () => {
    setupBannerCarousels();
});

function setupBannerCarousels() {
    // Define images per category
    const categoryImages = {
        "1": [
            'https://placehold.co/500x400/C8C8C8/424242?text=category+1+Image+1',
            'https://placehold.co/500x400/D3D3D3/424242?text=Category+1+Image+2',
            'https://placehold.co/500x400/B0C4DE/424242?text=Category+1+Image+3'
        ],
        "2": [
            'https://placehold.co/500x400/ADD8E6/424242?text=Category+2+Image+1',
            'https://placehold.co/500x400/F5DEB3/424242?text=Category+2+Image+2',
            'https://placehold.co/500x400/FFDAB9/424242?text=Category+2+Image+3'
        ],
        "3": [
            'https://placehold.co/500x400/90EE90/424242?text=Category+3+Image+1',
            'https://placehold.co/500x400/FFA07A/424242?text=Category+3+Image+2',
            'https://placehold.co/500x400/20B2AA/424242?text=Category+3+Image+3'
        ]
    };

    // Placeholder links for "Shop Now"
    const categoryLinks = {
        "1": "#", 
        "2": "#",
        "3": "#"
    };

    const sections = document.querySelectorAll('.banner-section');

    sections.forEach(section => {
        const category = section.dataset.category;
        const allImages = categoryImages[category] || [];
        const bannerLeft = section.querySelector('.banner-left');
        const bannerRight = section.querySelector('.banner-right');
        const dotsContainer = section.querySelector('.carousel-dots');
        const shopButton = section.querySelector('.shop-now-button');

        if (!bannerLeft || !bannerRight || !dotsContainer) return;

        // Set the shop link dynamically
        shopButton.href = categoryLinks[category];

        let currentIndex = 0;
        let autoplayInterval;
        let dots = [];

        const isMobile = () => window.innerWidth <= 768;

        const renderDots = () => {
            dotsContainer.innerHTML = "";
            const dotCount = isMobile()
                ? allImages.length
                : Math.ceil(allImages.length / 2);
            for (let i = 0; i < dotCount; i++) {
                const dot = document.createElement("span");
                dot.classList.add("dot");
                if (i === currentIndex) dot.classList.add("active");
                dot.dataset.index = i;
                dotsContainer.appendChild(dot);
            }
            dots = Array.from(dotsContainer.querySelectorAll(".dot"));
            dots.forEach(dot => {
                dot.addEventListener("click", (e) => {
                    currentIndex = parseInt(e.target.dataset.index);
                    updateBanners();
                    stopAutoplay();
                    startAutoplay();
                });
            });
        };

        const updateBanners = () => {
            const setBanner = (banner, mediaUrl) => {
                banner.innerHTML = "";
                banner.style.backgroundImage = "none";
                if (mediaUrl.endsWith(".mp4") || mediaUrl.endsWith(".webm")) {
                    const video = document.createElement("video");
                    video.src = mediaUrl;
                    video.controls = true;
                    video.preload = "metadata";
                    video.playsInline = true;
                    video.style.width = "100%";
                    video.style.height = "100%";
                    video.style.objectFit = "cover";
                    video.style.borderRadius = "10px";
                    banner.appendChild(video);
                    video.addEventListener("play", stopAutoplay);
                    video.addEventListener("ended", startAutoplay);
                    video.addEventListener("pause", () => {
                        if (video.currentTime < video.duration) startAutoplay();
                    });
                } else {
                    banner.style.backgroundImage = `url('${mediaUrl}')`;
                }
            };

            if (isMobile()) {
                setBanner(bannerLeft, allImages[currentIndex]);
                bannerRight.style.display = "none";
            } else {
                const leftMedia = allImages[currentIndex * 2];
                const rightMedia = allImages[currentIndex * 2 + 1];
                setBanner(bannerLeft, leftMedia);
                bannerLeft.style.display = "block";
                if (rightMedia) {
                    setBanner(bannerRight, rightMedia);
                    bannerRight.style.display = "block";
                } else {
                    bannerRight.style.display = "none";
                }
            }

            dots.forEach(dot => dot.classList.remove("active"));
            if (dots[currentIndex]) dots[currentIndex].classList.add("active");
        };

        const nextBanner = () => {
            const maxIndex = isMobile()
                ? allImages.length
                : Math.ceil(allImages.length / 2);
            currentIndex = (currentIndex + 1) % maxIndex;
            updateBanners();
        };

        const startAutoplay = () => {
            autoplayInterval = setInterval(nextBanner, 2500);
        };
        const stopAutoplay = () => {
            clearInterval(autoplayInterval);
            autoplayInterval = null;
        };

        renderDots();
        updateBanners();
        startAutoplay();

        [bannerLeft, bannerRight].forEach(banner => {
            banner.addEventListener('mouseenter', stopAutoplay);
            banner.addEventListener('mouseleave', startAutoplay);
        });

        window.addEventListener("resize", () => {
            currentIndex = 0;
            renderDots();
            updateBanners();
        });

        // Swipe support
        let startX = 0;
        let endX = 0;
        [bannerLeft, bannerRight].forEach(element => {
            element.addEventListener("touchstart", (e) => startX = e.touches[0].clientX);
            element.addEventListener("touchmove", (e) => e.preventDefault());
            element.addEventListener("touchend", (e) => {
                endX = e.changedTouches[0].clientX;
                const diff = startX - endX;
                if (Math.abs(diff) > 50) {
                    if (diff > 0) nextBanner();
                    else currentIndex = (currentIndex - 1 + (isMobile() ? allImages.length : Math.ceil(allImages.length / 2))) % (isMobile() ? allImages.length : Math.ceil(allImages.length / 2));
                    updateBanners();
                    stopAutoplay();
                    startAutoplay();
                }
                startX = 0;
                endX = 0;
            });
        });
    });
}

function setupProfileDropdown() {
    const profileBtn = document.getElementById("profile-btn");
    const profileMenu = document.getElementById("profile-menu");
    if (profileBtn && profileMenu) {
        profileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            profileMenu.classList.toggle("active");
        });
        document.addEventListener("click", (e) => {
            if (!profileMenu.contains(e.target) && !profileBtn.contains(e.target)) {
                profileMenu.classList.remove("active");
            }
        });
    }
}

function setupMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const closeMenuBtn = document.querySelector('.close-menu');
    if (menuToggle && mobileMenu && closeMenuBtn) {
        menuToggle.addEventListener('click', () => {
            mobileMenu.classList.add('active');
        });
        closeMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
        });
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) {
                mobileMenu.classList.remove('active');
            }
        });
    }
}

function setupLoginForgotModals() {
    const loginBtns = document.querySelectorAll(".login");
    loginBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            const loginModal = document.getElementById("login-popup");
            if (loginModal) {
                loginModal.classList.add("active");
                if (loginModal.addEventListener("click", (e) => {
                    if (e.target === loginModal) {
                        loginModal.classList.remove("active");
                    }
                }));
            }
        });
    });
}

function setupMobileProfileDropdown() {
    const mobileProfileBtn = document.querySelector(".mobile-profile-btn");
    const mobileDropdownMenu = document.querySelector(".mobile-dropdown-menu");
    if (mobileProfileBtn && mobileDropdownMenu) {
        mobileProfileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            mobileDropdownMenu.classList.toggle("active");
        });
        document.addEventListener("click", (e) => {
            if (!mobileDropdownMenu.contains(e.target) && !mobileProfileBtn.contains(e.target)) {
                mobileDropdownMenu.classList.remove("active");
            }
        });
    }
}

function setupNewsletterForm() {
    const form = document.querySelector(".newsletter");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });
            if (response.ok) {
                alert("Thank you for subscribing!");
                form.reset();
            } else {
                alert("Something went wrong. Try again.");
            }
        });
    }
}

function setupToastAutoRemove() {
    const toasts = document.querySelectorAll(".toast");
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.remove();
        }, 5000);
    });
}

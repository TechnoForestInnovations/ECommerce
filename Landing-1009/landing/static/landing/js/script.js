document.addEventListener('DOMContentLoaded', () => {

    /* -----------------------------------------------------
       🧭 0. Banner Carousels
    ----------------------------------------------------- */
    try {
        setupBannerCarousels();
    } catch (error) {
        console.error("Banner carousel error:", error);
    }

    /* -----------------------------------------------------
       🧭 1. Mobile Menu (Hamburger Toggle)
    ----------------------------------------------------- */
    try {
        const menuToggle = document.querySelector(".menu-toggle");
        const mobileMenu = document.querySelector(".mobile-menu");
        const closeMenuBtn = document.querySelector(".close-menu");

        if (menuToggle && mobileMenu) {
            menuToggle.addEventListener("click", (e) => {
                e.stopPropagation();
                mobileMenu.classList.add("active");
            });

            closeMenuBtn?.addEventListener("click", () => {
                mobileMenu.classList.remove("active");
            });

            mobileMenu.querySelectorAll("a").forEach(link => {
                link.addEventListener("click", () => {
                    mobileMenu.classList.remove("active");
                });
            });
        }

        document.addEventListener("click", (e) => {
            if (mobileMenu && !mobileMenu.contains(e.target) && e.target !== menuToggle) {
                mobileMenu.classList.remove("active");
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 768) {
                mobileMenu?.classList.remove("active");
            }
        });

    } catch (error) {
        console.error("Mobile menu error:", error);
    }

    /* -----------------------------------------------------
       👤 2. Profile Dropdown Menu (Desktop)
    ----------------------------------------------------- */
    try {
        const profileBtn = document.getElementById("profile-btn");
        const profileMenu = document.getElementById("profile-menu");

        if (profileBtn && profileMenu) {
            profileBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                profileMenu.classList.toggle("active");
            });

            document.addEventListener("click", (e) => {
                if (!profileMenu.contains(e.target) && e.target !== profileBtn) {
                    profileMenu.classList.remove("active");
                }
            });

            document.addEventListener("keydown", (e) => {
                if (e.key === "Escape") {
                    profileMenu.classList.remove("active");
                }
            });
        }
    } catch (error) {
        console.error("Profile dropdown error:", error);
    }

    /* -----------------------------------------------------
       💬 3. Login Popup Placeholder (for future use)
    ----------------------------------------------------- */
    

});

function setupBannerCarousels() {
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
                    video.muted = true;
                    video.autoplay = true;
                    video.loop = true;
                    video.playsInline = true;
                    video.style.width = "100%";
                    video.style.height = "100%";
                    video.style.objectFit = "cover";
                    video.style.borderRadius = "10px";
                    banner.appendChild(video);
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

        const stopAutoplay = () => clearInterval(autoplayInterval);

        renderDots();
        updateBanners();
        startAutoplay();

        // Remove hover-based pause — autoplay continues always

        window.addEventListener("resize", () => {
            currentIndex = 0;
            renderDots();
            updateBanners();
        });

        // Swipe support (still keeps autoplay running)
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
                }
                startX = 0;
                endX = 0;
            });
        });
    });
}


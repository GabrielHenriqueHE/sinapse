function openModal(modalId) {
            document.getElementById(modalId).classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Previne scroll da página
        }

        function closeModal(modalId) {
            document.getElementById(modalId).classList.add('hidden');
            document.body.style.overflow = 'auto'; // Restaura scroll
        }

        function switchToRegister() {
            closeModal('loginModal');
            setTimeout(() => openModal('registerModal'), 300);
        }

        function switchToLogin() {
            closeModal('registerModal');
            setTimeout(() => openModal('loginModal'), 300);
        }

        // Fechar modal ao clicar fora do conteúdo
        document.addEventListener('click', function(event) {
            const modals = ['loginModal', 'registerModal'];
            modals.forEach(modalId => {
                const modal = document.getElementById(modalId);
                if (event.target === modal) {
                    closeModal(modalId);
                }
            });
        });

        // Fechar modal com ESC
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const modals = ['loginModal', 'registerModal'];
                modals.forEach(modalId => {
                    if (!document.getElementById(modalId).classList.contains('hidden')) {
                        closeModal(modalId);
                    }
                });
            }
        });
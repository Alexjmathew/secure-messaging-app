document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat functionality
    const newChatBtn = document.getElementById('newChatBtn');
    const newChatBtn2 = document.getElementById('newChatBtn2');
    const newChatModal = document.getElementById('newChatModal');
    const closeModal = document.querySelector('.close-modal');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const userSearch = document.getElementById('userSearch');
    const userList = document.getElementById('userList');
    const contactsList = document.getElementById('contactsList');
    const chatArea = document.getElementById('chatArea');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    
    let currentChat = null;
    
    // Open new chat modal
    [newChatBtn, newChatBtn2].forEach(btn => {
        btn.addEventListener('click', () => {
            newChatModal.style.display = 'block';
            loadUsers();
        });
    });
    
    // Close modal
    closeModal.addEventListener('click', () => {
        newChatModal.style.display = 'none';
    });
    
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(tabId + 'Tab').classList.add('active');
        });
    });
    
    // Load users for new chat
    function loadUsers() {
        userList.innerHTML = '<div class="loading">Loading users...</div>';
        
        fetch('/api/users')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    userList.innerHTML = '';
                    
                    data.users.forEach(user => {
                        if (user.id !== currentUser.id) {
                            const userElement = document.createElement('div');
                            userElement.className = 'user-item';
                            userElement.innerHTML = `
                                <div class="avatar">
                                    <i class="fas fa-user"></i>
                                </div>
                                <div class="user-info">
                                    <h4>${user.email}</h4>
                                    <p class="status">${user.online ? 'Online' : 'Offline'}</p>
                                </div>
                            `;
                            
                            userElement.addEventListener('click', () => {
                                startNewChat(user.id);
                                newChatModal.style.display = 'none';
                            });
                            
                            userList.appendChild(userElement);
                        }
                    });
                } else {
                    userList.innerHTML = '<div class="error">Error loading users</div>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                userList.innerHTML = '<div class="error">Error loading users</div>';
            });
    }
    
    // Start a new chat
    function startNewChat(userId) {
        fetch('/api/chat/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentChat = data.chat_id;
                loadChat(data.chat_id);
                loadContacts();
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    // Load chat messages
    function loadChat(chatId) {
        chatArea.innerHTML = `
            <div class="loading-chat">
                <i class="fas fa-spinner fa-spin"></i> Loading chat...
            </div>
        `;
        
        fetch(`/api/chat/${chatId}/messages`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Load the chat template
                    fetch('/static/templates/chat.html')
                        .then(response => response.text())
                        .then(html => {
                            chatArea.innerHTML = html;
                            
                            // Initialize chat UI
                            const messagesContainer = document.getElementById('messagesContainer');
                            const chatWithName = document.getElementById('chatWithName');
                            
                            // Set chat participant name
                            const participant = data.participant;
                            chatWithName.textContent = participant.email;
                            
                            // Display messages
                            messagesContainer.innerHTML = '';
                            data.messages.forEach(msg => {
                                const messageElement = document.createElement('div');
                                messageElement.className = `message ${msg.sender === currentUser.id ? 'sent' : 'received'}`;
                                messageElement.innerHTML = `
                                    <div class="message-content">${msg.content}</div>
                                    <div class="message-time">${formatTime(msg.timestamp)}</div>
                                `;
                                messagesContainer.appendChild(messageElement);
                            });
                            
                            // Scroll to bottom
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
                            
                            // Set up message sending
                            setupMessageSending(chatId);
                        });
                }
            })
            .catch(error => console.error('Error:', error));
    }
    
    // Set up message sending
    function setupMessageSending(chatId) {
        const messageInput = document.getElementById('messageInput');
        const sendMessageBtn = document.getElementById('sendMessageBtn');
        
        sendMessageBtn.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        function sendMessage() {
            const content = messageInput.value.trim();
            if (content && chatId) {
                fetch(`/api/chat/${chatId}/send`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ content: content })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        messageInput.value = '';
                        loadChat(chatId);
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        }
    }
    
    // Format time
    function formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Initial load
    loadContacts();
    
    // Load contacts list
    function loadContacts() {
        contactsList.innerHTML = '<div class="loading">Loading contacts...</div>';
        
        fetch('/api/contacts')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    contactsList.innerHTML = '';
                    
                    data.contacts.forEach(contact => {
                        const contactElement = document.createElement('div');
                        contactElement.className = 'contact-item';
                        contactElement.innerHTML = `
                            <div class="avatar">
                                <i class="fas fa-user"></i>
                            </div>
                            <div class="contact-info">
                                <h4>${contact.email}</h4>
                                <p class="last-message">${contact.last_message || 'No messages yet'}</p>
                            </div>
                            <div class="contact-time">${contact.last_message_time ? formatTime(contact.last_message_time) : ''}</div>
                        `;
                        
                        contactElement.addEventListener('click', () => {
                            loadChat(contact.chat_id);
                        });
                        
                        contactsList.appendChild(contactElement);
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                contactsList.innerHTML = '<div class="error">Error loading contacts</div>';
            });
    }
});

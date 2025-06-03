// Client-side encryption using Web Crypto API
class SecureEncryption {
    static async deriveKey(password, salt) {
        const keyMaterial = await window.crypto.subtle.importKey(
            'raw',
            new TextEncoder().encode(password),
            { name: 'PBKDF2' },
            false,
            ['deriveKey']
        );
        
        return await window.crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: salt,
                iterations: 100000,
                hash: 'SHA-512'
            },
            keyMaterial,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
    }
    
    static async encrypt(message, password) {
        const salt = window.crypto.getRandomValues(new Uint8Array(16));
        const iv = window.crypto.getRandomValues(new Uint8Array(12));
        const key = await this.deriveKey(password, salt);
        
        const encrypted = await window.crypto.subtle.encrypt(
            {
                name: 'AES-GCM',
                iv: iv
            },
            key,
            new TextEncoder().encode(message)
        );
        
        // Combine salt + iv + ciphertext
        const combined = new Uint8Array(salt.byteLength + iv.byteLength + encrypted.byteLength);
        combined.set(salt, 0);
        combined.set(iv, salt.byteLength);
        combined.set(new Uint8Array(encrypted), salt.byteLength + iv.byteLength);
        
        return btoa(String.fromCharCode.apply(null, combined));
    }
    
    static async decrypt(encrypted, password) {
        const combined = new Uint8Array(atob(encrypted).split('').map(c => c.charCodeAt(0)));
        const salt = combined.slice(0, 16);
        const iv = combined.slice(16, 28);
        const ciphertext = combined.slice(28);
        
        const key = await this.deriveKey(password, salt);
        
        try {
            const decrypted = await window.crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: iv
                },
                key,
                ciphertext
            );
            
            return new TextDecoder().decode(decrypted);
        } catch (e) {
            console.error('Decryption failed:', e);
            return null;
        }
    }
}


VERSION = '1.0.1'
LAST_UPDATE = '2025-03-13'
CHANGES = {
    '1.0.1': [
        'Hata yakalama ve loglama sistemi geliştirildi',
        'Sayfa yükleme ve element kontrolü güçlendirildi',
        'Text input için yeni retry mekanizması eklendi'
    ],
    '1.0.0': [
        'İlk versiyon'
    ]
}

def get_version_info():
    """Get formatted version info string"""
    return f"PrezzoVoice Bot v{VERSION} ({LAST_UPDATE})"

def get_changes():
    """Get formatted changelog string"""
    changes = []
    for version, items in CHANGES.items():
        changes.append(f"\nVersion {version}:")
        changes.extend([f"- {item}" for item in items])
    return "\n".join(changes)

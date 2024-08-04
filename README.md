# HM Message Relay Bot

MessageRelayBot, Discord botu olup belirli kanallar arasında mesaj iletimini sağlar. Mesaj yönlendirme, düzenleme ve silme gibi özellikler sunar ve sunucu yöneticilerine komutlar aracılığıyla kanalları yönetme ve mesaj yönlendirmeyi kontrol etme imkanı verir.

## Özellikler

- **Mesaj Yönlendirme:** Kaynak kanallardan hedef kanallara otomatik mesaj iletimi yapar.
- **Mesaj Düzenleme:** Orijinal mesaj düzenlendiğinde, iletilen mesajı günceller.
- **Mesaj Silme:** Orijinal mesaj silindiğinde, iletilen mesajı günceller.
- **Kanal Yönetimi:** Kaynak ve hedef kanalları ekleme veya çıkarma işlemleri sağlar.
- **Yönlendirmeyi Kontrol Etme:** Mesaj yönlendirmeyi açma veya kapama.
- **Sunucu Bilgisi:** Sunucu ile ilgili bilgiler ve davet linklerini gösterir.

## Kurulum

1. **Depoyu klonlayın:**

   ```bash
   git clone https://github.com/liseliyalayan131/Discord-Message-Relay-Bot.git
   ```

2. **Bağımlılıkları yükleyin:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ortam değişkenlerinizi yapılandırın:**

   `example.env` dosyasını `.env` olarak yeniden adlandırın ve Discord token'ınızı ve diğer yapılandırma ayrıntılarını girin.

4. **Botu çalıştırın:**

   Sağlanan batch dosyasını kullanarak botu başlatın:

   ```bash
   start.bat
   ```

## Komutlar

- `!toggle_forwarding` - Mesaj yönlendirmeyi açma veya kapama.
- `!add_channels <source_id> <target_id>` - Kaynak ve hedef kanalları ekler.
- `!status` - Mevcut mesaj yönlendirme durumu ve kanal listelerini gösterir.
- `!remove_channel <channel_id>` - Kaynak veya hedef listesinden bir kanalı çıkarır.
- `!set_role <command_name> <role>` - Bir komuta rol atar.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - ayrıntılar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

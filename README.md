# İhale MCP: Türkiye Kamu İhaleleri için MCP Sunucusu

Bu proje, Türkiye'deki kamu ihalelerine (`ekap.kik.gov.tr`) erişimi kolaylaştıran bir [FastMCP](https://gofastmcp.com/) sunucusu oluşturur. Bu sayede, EKAP v2 portalından ihale arama, ihale detaylarını getirme ve ihale duyurularını Markdown formatında alma işlemleri, Model Context Protocol (MCP) destekleyen LLM (Büyük Dil Modeli) uygulamaları (örneğin Claude Desktop veya [5ire](https://5ire.app)) ve diğer istemciler tarafından araç (tool) olarak kullanılabilir hale gelir.

🎯 **Temel Özellikler**

* EKAP v2 portalına programatik erişim için standart bir MCP arayüzü.
* Aşağıdaki yetenekler:
    * **Detaylı İhale Arama:** İhale adı/içeriği, IKN numarası, ihale türü, il, tarih aralıkları ve 17+ boolean filtre ile kapsamlı arama.
    * **İhale Detayları:** Belirli bir ihalenin tam detaylarını (özellikler, OKAS kodları, idare bilgileri, işlem kuralları) getirme.
    * **İhale Duyuruları:** İhale ile ilgili tüm duyuruları (Ön İlan, İhale İlanı, Sonuç İlanı vb.) otomatik HTML-to-Markdown dönüşümü ile getirme.
    * **OKAS Kod Arama:** Türk kamu alım sınıflandırma kodlarında arama yapma.
    * **İdare Arama:** Bakanlık, belediye, üniversite gibi kamu kurumlarını arama.
* İhale metinlerinin LLM'ler tarafından daha kolay işlenebilmesi için HTML'den Markdown formatına çevrilmesi.
* Claude Desktop uygulaması ile kolay entegrasyon.
* İhale MCP, [5ire](https://5ire.app) gibi Claude Desktop haricindeki MCP istemcilerini de destekler.

---
🚀 **Claude Haricindeki Modellerle Kullanmak İçin Çok Kolay Kurulum (Örnek: 5ire için)**

Bu bölüm, İhale MCP aracını 5ire gibi Claude Desktop dışındaki MCP istemcileriyle kullanmak isteyenler içindir.

* **Python Kurulumu:** Sisteminizde Python 3.11 veya üzeri kurulu olmalıdır. Kurulum sırasında "**Add Python to PATH**" (Python'ı PATH'e ekle) seçeneğini işaretlemeyi unutmayın. [Buradan](https://www.python.org/downloads/) indirebilirsiniz.
* **Git Kurulumu (Windows):** Bilgisayarınıza [git](https://git-scm.com/downloads/win) yazılımını indirip kurun. "Git for Windows/x64 Setup" seçeneğini indirmelisiniz.
* **`uv` Kurulumu:**
    * **Windows Kullanıcıları (PowerShell):** Bir CMD ekranı açın ve bu kodu çalıştırın: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
    * **Mac/Linux Kullanıcıları (Terminal):** Bir Terminal ekranı açın ve bu kodu çalıştırın: `curl -LsSf https://astral.sh/uv/install.sh | sh`
* **Microsoft Visual C++ Redistributable (Windows):** Bazı Python paketlerinin doğru çalışması için gereklidir. [Buradan](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) indirip kurun.
* İşletim sisteminize uygun [5ire](https://5ire.app) MCP istemcisini indirip kurun.
* 5ire'ı açın. **Workspace -> Providers** menüsünden kullanmak istediğiniz LLM servisinin API anahtarını girin.
* **Tools** menüsüne girin. **+Local** veya **New** yazan butona basın.
    * **Tool Key:** `ihalemcp`
    * **Name:** `İhale MCP`
    * **Command:**
        ```
        uvx ihale-mcp
        ```
    * **Save** butonuna basarak kaydedin.
* Şimdi **Tools** altında **İhale MCP**'yi görüyor olmalısınız. Üstüne geldiğinizde sağda çıkan butona tıklayıp etkinleştirin (yeşil ışık yanmalı).
* Artık İhale MCP ile konuşabilirsiniz.

---
⚙️ **Claude Desktop Manuel Kurulumu**

1.  **Ön Gereksinimler:** Python, `uv`, (Windows için) Microsoft Visual C++ Redistributable'ın sisteminizde kurulu olduğundan emin olun. Detaylı bilgi için yukarıdaki "5ire için Kurulum" bölümündeki ilgili adımlara bakabilirsiniz.
2.  Claude Desktop **Settings -> Developer -> Edit Config**.
3.  Açılan `claude_desktop_config.json` dosyasına `mcpServers` altına ekleyin:

    ```json
    {
      "mcpServers": {
        "İhale MCP": {
          "command": "uvx",
          "args": [
            "ihale-mcp"
          ]
        }
      }
    }
    ```
4.  Claude Desktop'ı kapatıp yeniden başlatın.

🛠️ **Kullanılabilir Araçlar (MCP Tools)**

Bu FastMCP sunucusu LLM modelleri için aşağıdaki araçları sunar:

* **`search_tenders`**: EKAP v2 portalında kapsamlı ihale arama yapar.
    * **Ana Parametreler**: `search_text`, `ikn_year`, `ikn_number`, `tender_types`, `tender_date_start/end`, `announcement_date_start/end`
    * **Boolean Filtreler**: `e_ihale`, `ortak_alim_mi`, `kismi_teklif_mi`, `yabanci_isteklilere_izin_veriliyor_mu` ve 13+ daha fazla filtre
    * **Liste Filtreleri**: `provinces`, `tender_statuses`, `tender_methods`, `okas_codes`, `authority_ids`, `proposal_types`, `announcement_types`
    * **Arama Kapsamı**: `search_in_title`, `search_in_announcement`, `search_in_tech_spec` vb. 11 farklı alan
    * **Döndürdüğü Değer**: Sayfalanmış ihale listesi, toplam sonuç sayısı

* **`search_okas_codes`**: OKAS (kamu alım sınıflandırma) kodlarında arama yapar.
    * **Parametreler**: `search_term`, `kalem_turu` (1=Mal, 2=Hizmet, 3=Yapım), `limit`
    * **Döndürdüğü Değer**: OKAS kodları, açıklamaları ve kategorileri

* **`search_authorities`**: Türk kamu kurumlarında arama yapar.
    * **Parametreler**: `search_term`, `limit`
    * **Döndürdüğü Değer**: Kurum ID'leri, isimleri ve hiyerarşik bilgileri

* **`get_recent_tenders`**: Son N gündeki ihaleleri getirir.
    * **Parametreler**: `days` (1-30), `tender_types`, `limit`
    * **Döndürdüğü Değer**: Yakın tarihli ihale listesi

* **`get_tender_announcements`**: Belirli bir ihalenin tüm duyurularını getirir.
    * **Parametreler**: `tender_id`, `include_html`
    * **Döndürdüğü Değer**: Otomatik HTML-to-Markdown dönüştürülmüş ihale duyuruları

* **`get_tender_details`**: Belirli bir ihalenin kapsamlı detaylarını getirir.
    * **Parametreler**: `tender_id`
    * **Döndürdüğü Değer**: İhale özellikleri, OKAS kodları, idare bilgileri, işlem kuralları ve otomatik markdown'a çevrilmiş duyuru özetleri

## İhale Türleri

- **1 - Mal**: Malzeme ve ekipman alımları
- **2 - Yapım**: İnşaat ve altyapı projeleri  
- **3 - Hizmet**: Hizmet sözleşmeleri
- **4 - Danışmanlık**: Danışmanlık hizmetleri

## Örnek Kullanımlar

1. **Pazar Araştırması**: Belirli sektör veya bölgelerdeki fırsatları takip etme
2. **Uygunluk İzleme**: Mevzuata uygunluk için ihale duyurularını takip etme
3. **İş Zekası**: Kamu harcama modellerini ve trendlerini analiz etme
4. **Bildirim Sistemleri**: Belirli ihale türleri için uyarı sistemleri kurma
5. **Veri Analizi**: Araştırma ve analiz için ihale verilerini çıkarma

## Yeni Özellikler

✅ **17+ Boolean Filtre**: e-İhale, ortak alım, kısmi teklif, yabancı katılım vb.
✅ **Liste Filtreleri**: İller, ihale durumları, usulleri, OKAS kodları, idare ID'leri
✅ **Arama Kapsamı Kontrolü**: IKN, başlık, duyuru, teknik şartname vb. alanlarda arama
✅ **İdare Arama**: 72,000+ kamu kurumunda arama (bakanlık, belediye, üniversite)
✅ **İhale Duyuruları**: Otomatik HTML-to-Markdown dönüşümü ile tam duyuru metinleri
✅ **Kapsamlı İhale Detayları**: Tüm ihale metadata'sı, özellikler, kurallar bir arada

## API Hız Limitleri

Bu sunucu EKAP portalının hız limitlerini gözetir. Üretim kullanımı için aşağıdakileri göz önünde bulundurun:
- API çağrılarını azaltmak için istek önbellekleme
- Üstel geri çekilme ile yeniden deneme mantığı
- Yüksek hacimli kullanım için istek sırası

📜 **Lisans**

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

## Sorumluluk Reddi

Bu, Türk hükümetinin EKAP portalı ile resmi olmayan bir entegrasyondır. Kullanıcılar portalın hizmet şartlarına ve geçerli düzenlemelere uymakla yükümlüdür. Yazarlar Türk hükümeti veya EKAP portalı ile bağlantılı değildir.
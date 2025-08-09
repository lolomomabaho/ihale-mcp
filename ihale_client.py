#!/usr/bin/env python3
"""
EKAP v2 API client for Turkish government tender/procurement data - FIXED VERSION
"""

import httpx
import ssl
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
from io import BytesIO
from markitdown import MarkItDown

class EKAPClient:
    """Client for EKAP v2 API"""
    
    def __init__(self):
        self.base_url = "https://ekapv2.kik.gov.tr"
        self.tender_endpoint = "/b_ihalearama/api/Ihale/GetListByParameters"
        self.okas_endpoint = "/b_ihalearama/api/IhtiyacKalemleri/GetAll"
        self.authority_endpoint = "/b_idare/api/DetsisKurumBirim/DetsisAgaci"
        self.announcements_endpoint = "/b_ihalearama/api/Ilan/GetList"
        self.tender_details_endpoint = "/b_ihalearama/api/IhaleDetay/GetByIhaleIdIhaleDetay"
        
        # Common headers for all requests
        self.headers = {
            'Accept': 'application/json',
            'Accept-Language': 'null',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://ekapv2.kik.gov.tr',
            'Referer': 'https://ekapv2.kik.gov.tr/ekap/search',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'api-version': 'v1',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context that supports older protocols"""
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context
    
    async def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make an API request to EKAP v2"""
        ssl_context = self._create_ssl_context()
        
        async with httpx.AsyncClient(
            timeout=30.0,
            verify=ssl_context,
            http2=False,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        ) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                json=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    def _format_date_for_api(self, date_str: Optional[str]) -> Optional[str]:
        """Convert YYYY-MM-DD to DD.MM.YYYY format expected by API"""
        if not date_str:
            return None
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d.%m.%Y")
        except ValueError:
            return None
    
    async def search_tenders(
        self,
        search_text: str = "",
        ikn_year: Optional[int] = None,
        ikn_number: Optional[int] = None,
        tender_types: List[int] = None,
        tender_date_start: Optional[str] = None,
        tender_date_end: Optional[str] = None,
        announcement_date_start: Optional[str] = None,
        announcement_date_end: Optional[str] = None,
        search_type: Literal["GirdigimGibi", "TumKelimeler"] = "GirdigimGibi",
        order_by: Literal["ihaleTarihi", "ihaleAdi", "idareAdi"] = "ihaleTarihi",
        sort_order: Literal["asc", "desc"] = "desc",
        # Boolean filters
        e_ihale: Optional[bool] = None,
        e_eksiltme_yapilacak_mi: Optional[bool] = None,
        ortak_alim_mi: Optional[bool] = None,
        kismi_teklif_mi: Optional[bool] = None,
        fiyat_disi_unsur_varmi: Optional[bool] = None,
        ekonomik_mali_yeterlilik_belgeleri_isteniyor_mu: Optional[bool] = None,
        mesleki_teknik_yeterlilik_belgeleri_isteniyor_mu: Optional[bool] = None,
        is_deneyimi_gosteren_belgeler_isteniyor_mu: Optional[bool] = None,
        yerli_istekliye_fiyat_avantaji_uygulanıyor_mu: Optional[bool] = None,
        yabanci_isteklilere_izin_veriliyor_mu: Optional[bool] = None,
        alternatif_teklif_verilebilir_mi: Optional[bool] = None,
        konsorsiyum_katilabilir_mi: Optional[bool] = None,
        alt_yuklenici_calistirilabilir_mi: Optional[bool] = None,
        fiyat_farki_verilecek_mi: Optional[bool] = None,
        avans_verilecek_mi: Optional[bool] = None,
        cerceve_anlasmasi_mi: Optional[bool] = None,
        personel_calistirilmasina_dayali_mi: Optional[bool] = None,
        # List filters
        provinces: List[int] = None,
        tender_statuses: List[int] = None,
        tender_methods: List[int] = None,
        tender_sub_methods: List[int] = None,
        okas_codes: List[str] = None,
        authority_ids: List[int] = None,
        proposal_types: List[int] = None,
        announcement_types: List[int] = None,
        # Search scope parameters
        search_in_ikn: bool = True,
        search_in_title: bool = True,
        search_in_announcement: bool = True,
        search_in_tech_spec: bool = True,
        search_in_admin_spec: bool = True,
        search_in_similar_work: bool = True,
        search_in_location: bool = True,
        search_in_nature_quantity: bool = True,
        search_in_tender_info: bool = True,
        search_in_contract_draft: bool = True,
        search_in_bid_form: bool = True,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search for Turkish government tenders"""
        
        # Build API request payload
        api_params = {
            "searchText": search_text,
            "filterType": None,
            "ikNdeAra": search_in_ikn,
            "ihaleAdindaAra": search_in_title,
            "ihaleIlanindaAra": search_in_announcement,
            "teknikSartnamedeAra": search_in_tech_spec,
            "idariSartnamedeAra": search_in_admin_spec,
            "benzerIsMaddesindeAra": search_in_similar_work,
            "isinYapilacagiYerMaddesindeAra": search_in_location,
            "nitelikTurMiktarMaddesindeAra": search_in_nature_quantity,
            "ihaleBilgilerindeAra": search_in_tender_info,
            "sozlesmeTasarisindaAra": search_in_contract_draft,
            "teklifCetvelindeAra": search_in_bid_form,
            "searchType": search_type,
            "iknYili": ikn_year,
            "iknSayi": ikn_number,
            "ihaleTarihSaatBaslangic": self._format_date_for_api(tender_date_start),
            "ihaleTarihSaatBitis": self._format_date_for_api(tender_date_end),
            "ilanTarihSaatBaslangic": self._format_date_for_api(announcement_date_start),
            "ilanTarihSaatBitis": self._format_date_for_api(announcement_date_end),
            "yasaKapsami4734List": [],
            "ihaleTuruIdList": tender_types or [],
            "ihaleUsulIdList": tender_methods or [],
            "ihaleUsulAltIdList": tender_sub_methods or [],
            "ihaleIlIdList": provinces or [],
            "ihaleDurumIdList": tender_statuses or [],
            "idareIdList": authority_ids or [],
            "ihaleIlanTuruIdList": announcement_types or [],
            "teklifTuruIdList": proposal_types or [],
            "asiriDusukTeklifIdList": [],
            "istisnaMaddeIdList": [],
            "okasBransKodList": okas_codes or [],
            "okasBransAdiList": [],
            "titubbKodList": [],
            "gmdnKodList": [],
            # Boolean filters
            "eIhale": e_ihale,
            "eEksiltmeYapilacakMi": e_eksiltme_yapilacak_mi,
            "ortakAlimMi": ortak_alim_mi,
            "kismiTeklifMi": kismi_teklif_mi,
            "fiyatDisiUnsurVarmi": fiyat_disi_unsur_varmi,
            "ekonomikVeMaliYeterlilikBelgeleriIsteniyorMu": ekonomik_mali_yeterlilik_belgeleri_isteniyor_mu,
            "meslekiTeknikYeterlilikBelgeleriIsteniyorMu": mesleki_teknik_yeterlilik_belgeleri_isteniyor_mu,
            "isDeneyimiGosterenBelgelerIsteniyorMu": is_deneyimi_gosteren_belgeler_isteniyor_mu,
            "yerliIstekliyeFiyatAvantajiUgulaniyorMu": yerli_istekliye_fiyat_avantaji_uygulanıyor_mu,
            "yabanciIsteklilereIzinVeriliyorMu": yabanci_isteklilere_izin_veriliyor_mu,
            "alternatifTeklifVerilebilirMi": alternatif_teklif_verilebilir_mi,
            "konsorsiyumKatilabilirMi": konsorsiyum_katilabilir_mi,
            "altYukleniciCalistirilabilirMi": alt_yuklenici_calistirilabilir_mi,
            "fiyatFarkiVerilecekMi": fiyat_farki_verilecek_mi,
            "avansVerilecekMi": avans_verilecek_mi,
            "cerceveAnlasmaMi": cerceve_anlasmasi_mi,
            "personelCalistirilmasinaDayaliMi": personel_calistirilmasina_dayali_mi,
            "orderBy": order_by,
            "siralamaTipi": sort_order,
            "paginationSkip": skip,
            "paginationTake": limit
        }
        
        try:
            # Make API request
            response_data = await self._make_request(self.tender_endpoint, api_params)
            
            # Parse and format the response
            tenders = response_data.get("list", [])
            total_count = response_data.get("totalCount", 0)
            
            # Format each tender for better readability
            formatted_tenders = []
            for tender in tenders:
                formatted_tender = {
                    "id": tender.get("id"),
                    "name": tender.get("ihaleAdi"),
                    "ikn": tender.get("ikn"),
                    "type": {
                        "code": tender.get("ihaleTip"),
                        "description": tender.get("ihaleTipAciklama")
                    },
                    "method": tender.get("ihaleUsulAciklama"),
                    "status": {
                        "code": tender.get("ihaleDurum"),
                        "description": tender.get("ihaleDurumAciklama")
                    },
                    "authority": tender.get("idareAdi"),
                    "province": tender.get("ihaleIlAdi"),
                    "tender_datetime": tender.get("ihaleTarihSaat"),
                    "document_count": tender.get("dokumanSayisi", 0),
                    "has_announcement": tender.get("ilanVarMi", False),
                    "ekap_url": f"https://ekapv2.kik.gov.tr/ekap/tender/{tender.get('id')}" if tender.get('id') else None
                }
                formatted_tenders.append(formatted_tender)
            
            return {
                "tenders": formatted_tenders,
                "total_count": total_count,
                "returned_count": len(formatted_tenders)
            }
            
        except httpx.HTTPStatusError as e:
            return {
                "error": f"API request failed with status {e.response.status_code}",
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": "Request failed",
                "message": str(e)
            }
    
    async def search_okas_codes(
        self,
        search_term: str = "",
        kalem_turu: Optional[Literal[1, 2, 3]] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Search OKAS (public procurement classification) codes"""
        
        # Validate limit
        if limit > 500:
            limit = 500
        elif limit < 1:
            limit = 1
        
        # Build API request payload for OKAS search
        okas_params = {
            "loadOptions": {
                "filter": {
                    "sort": [],
                    "group": [],
                    "filter": [],
                    "totalSummary": [],
                    "groupSummary": [],
                    "select": [],
                    "preSelect": [],
                    "primaryKey": []
                }
            }
        }
        
        # Add search filters if provided
        filters = []
        
        if search_term:
            # Search in both Turkish and English descriptions
            filters.extend([
                ["kalemAdi", "contains", search_term],
                "or",
                ["kalemAdiEng", "contains", search_term]
            ])
        
        # Note: kalem_turu filtering causes 500 errors on the API
        # We'll filter client-side after getting results
        
        if filters:
            okas_params["loadOptions"]["filter"]["filter"] = filters
        
        # Set take limit for API
        okas_params["loadOptions"]["take"] = limit
        
        try:
            # Make API request to OKAS endpoint
            response_data = await self._make_request(self.okas_endpoint, okas_params)
            
            # Parse and format the response
            okas_items = response_data.get("loadResult", {}).get("data", [])
            
            # Format each OKAS code for better readability
            results = []
            for item in okas_items:
                kalem_turu_desc = {
                    1: "Mal (Goods)",
                    2: "Hizmet (Service)", 
                    3: "Yapım (Construction)"
                }.get(item.get("kalemTuru"), "Unknown")
                
                # Client-side filtering by kalem_turu since API filtering causes 500 errors
                if kalem_turu is not None and item.get("kalemTuru") != kalem_turu:
                    continue
                
                results.append({
                    "id": item.get("id"),
                    "code": item.get("kod"),
                    "description_tr": item.get("kalemAdi"),
                    "description_en": item.get("kalemAdiEng"),
                    "item_type": {
                        "code": item.get("kalemTuru"),
                        "description": kalem_turu_desc
                    },
                    "code_level": item.get("kodLevel"),
                    "parent_id": item.get("parentId"),
                    "has_items": item.get("hasItem", False),
                    "child_count": item.get("childCount", 0)
                })
            
            # Apply limit after client-side filtering
            if len(results) > limit:
                results = results[:limit]
            
            return {
                "okas_codes": results,
                "total_found": len(results),
                "search_params": {
                    "search_term": search_term,
                    "kalem_turu": kalem_turu,
                    "limit": limit
                },
                "item_type_legend": {
                    "1": "Mal (Goods)",
                    "2": "Hizmet (Service)",
                    "3": "Yapım (Construction)"
                }
            }
            
        except httpx.HTTPStatusError as e:
            return {
                "error": f"API request failed with status {e.response.status_code}",
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": "Request failed",
                "message": str(e)
            }
    
    async def search_authorities(
        self,
        search_term: str = "",
        limit: int = 50
    ) -> Dict[str, Any]:
        """Search Turkish government authorities/institutions"""
        
        # Validate limit
        if limit > 500:
            limit = 500
        elif limit < 1:
            limit = 1
        
        # Build API request payload for authority search
        authority_params = {
            "loadOptions": {
                "filter": {
                    "sort": [],
                    "group": [],
                    "filter": [],
                    "totalSummary": [],
                    "groupSummary": [],
                    "select": [],
                    "preSelect": [],
                    "primaryKey": []
                }
            }
        }
        
        # Add search filters if provided
        filters = []
        
        if search_term:
            # Search in authority names (correct field name is 'ad')
            filters.append(["ad", "contains", search_term])
        
        if filters:
            authority_params["loadOptions"]["filter"]["filter"] = filters
        
        # Set take limit for API
        authority_params["loadOptions"]["take"] = limit
        
        try:
            # Make API request to authority endpoint
            response_data = await self._make_request(self.authority_endpoint, authority_params)
            
            # Parse and format the response
            authority_items = response_data.get("loadResult", {}).get("data", [])
            
            # Format each authority for better readability
            results = []
            for item in authority_items:
                results.append({
                    "id": item.get("id"),
                    "name": item.get("ad"),
                    "parent_id": item.get("parentIdareKimlikKodu"),
                    "level": item.get("seviye"),
                    "has_children": item.get("hasItems", False),
                    "child_count": 0,  # Not available in response
                    "detsis_no": item.get("detsisNo"),
                    "idare_id": item.get("idareId")
                })
            
            return {
                "authorities": results,
                "total_found": len(results),
                "search_params": {
                    "search_term": search_term,
                    "limit": limit
                }
            }
            
        except httpx.HTTPStatusError as e:
            return {
                "error": f"API request failed with status {e.response.status_code}",
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": "Request failed - authority search",
                "message": str(e)
            }
    
    async def get_tender_announcements(
        self,
        tender_id: int
    ) -> Dict[str, Any]:
        """Get all announcements for a specific tender"""
        
        # Build API request payload for announcements
        announcement_params = {
            "ihaleId": tender_id
        }
        
        try:
            # Make API request to announcements endpoint
            response_data = await self._make_request(self.announcements_endpoint, announcement_params)
            
            # Parse and format the response
            announcements = response_data.get("list", [])
            
            # Initialize markdown converter (always convert)
            markitdown = MarkItDown()
            
            # Format each announcement for better readability
            results = []
            for announcement in announcements:
                # Map announcement types
                announcement_type_map = {
                    "1": "Ön İlan",
                    "2": "İhale İlanı",
                    "3": "İptal İlanı",
                    "4": "Sonuç İlanı",
                    "5": "Ön Yeterlik İlanı",
                    "6": "Düzeltme İlanı"
                }
                
                announcement_type = announcement.get("ilanTip", "")
                announcement_type_desc = announcement_type_map.get(announcement_type, f"Type {announcement_type}")
                
                html_content = announcement.get("veriHtml", "")
                
                # Always convert HTML to markdown
                markdown_content = None
                if html_content:
                    try:
                        # Create BytesIO from HTML content
                        html_bytes = BytesIO(html_content.encode('utf-8'))
                        result = markitdown.convert_stream(html_bytes, file_extension=".html")
                        markdown_content = result.text_content if result else None
                    except Exception as e:
                        print(f"Warning: Failed to convert HTML to markdown: {e}")
                        markdown_content = None
                
                results.append({
                    "id": announcement.get("id"),
                    "type": {
                        "code": announcement_type,
                        "description": announcement_type_desc
                    },
                    "title": announcement.get("baslik"),
                    "date": announcement.get("ilanTarihi"),
                    "status": announcement.get("status"),
                    "tender_id": announcement.get("ihaleId"),
                    "contract_id": announcement.get("sozlesmeId"),
                    "bidder_name": announcement.get("istekliAdi"),
                    "html_content": html_content,
                    "markdown_content": markdown_content,
                    "content_preview": self._extract_text_preview(html_content)
                })
            
            return {
                "announcements": results,
                "total_count": len(results),
                "tender_id": tender_id
            }
            
        except httpx.HTTPStatusError as e:
            return {
                "error": f"API request failed with status {e.response.status_code}",
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": "Request failed - tender announcements",
                "message": str(e)
            }
    
    def _extract_text_preview(self, html_content: str, max_length: int = 200) -> str:
        """Extract plain text preview from HTML content"""
        if not html_content:
            return ""
        
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    async def get_tender_details(
        self,
        tender_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive details for a specific tender"""
        
        # Build API request payload for tender details
        details_params = {
            "ihaleId": str(tender_id)
        }
        
        try:
            # Make API request to tender details endpoint
            response_data = await self._make_request(self.tender_details_endpoint, details_params)
            
            # Parse and format the response
            item = response_data.get("item", {})
            
            if not item:
                return {
                    "error": "Tender details not found",
                    "tender_id": tender_id
                }
            
            # Format tender characteristics
            characteristics = []
            for char in item.get("ihaleOzellikList", []):
                char_text = char.get("ihaleOzellik", "")
                # Clean up the characteristic text
                if "TENDER_DETAIL." in char_text:
                    char_text = char_text.replace("TENDER_DETAIL.", "").replace("_", " ").title()
                characteristics.append(char_text)
            
            # Format basic tender info
            basic_info = item.get("ihaleBilgi", {})
            
            # Format OKAS codes
            okas_codes = []
            for okas in item.get("ihtiyacKalemiOkasList", []):
                okas_codes.append({
                    "code": okas.get("kodu"),
                    "name": okas.get("adi"),
                    "full_description": okas.get("koduAdi")
                })
            
            # Format authority info
            authority = item.get("idare", {})
            authority_info = {
                "id": authority.get("id"),
                "name": authority.get("adi"),
                "code1": authority.get("kod1"),
                "code2": authority.get("kod2"),
                "phone": authority.get("telefon"),
                "fax": authority.get("fax"),
                "parent_authority": authority.get("ustIdare"),
                "top_authority_code": authority.get("enUstIdareKod"),
                "top_authority_name": authority.get("enUstIdareAdi"),
                "province": authority.get("il", {}).get("adi"),
                "district": authority.get("ilce", {}).get("ilceAdi")
            }
            
            # Format process rules
            rules = item.get("islemlerKuralSeti", {})
            process_rules = {
                "can_download_documents": rules.get("dokumanIndirmisMi", False),
                "has_submitted_bid": rules.get("teklifteBulunmusMu", False),
                "can_submit_bid": rules.get("teklifVerilebilirMi", False),
                "has_non_price_factors": rules.get("fiyatDisiUnsurVarMi", False),
                "contract_signed": rules.get("sozlesmeImzaliMi", False),
                "is_electronic": rules.get("eIhaleMi", False),
                "is_own_tender": rules.get("idareKendiIhaleMi", False),
                "electronic_auction": rules.get("eEksiltmeYapilacakMi", False)
            }
            
            # Initialize markdown converter for tender details HTML content
            markitdown = MarkItDown()
            
            # Format announcements list (basic info) with markdown conversion
            announcements = []
            for announcement in item.get("ilanList", []):
                # Map announcement types
                announcement_type_map = {
                    "1": "Ön İlan",
                    "2": "İhale İlanı", 
                    "3": "İptal İlanı",
                    "4": "Sonuç İlanı",
                    "5": "Ön Yeterlik İlanı",
                    "6": "Düzeltme İlanı"
                }
                
                announcement_type = announcement.get("ilanTip", "")
                announcement_type_desc = announcement_type_map.get(announcement_type, f"Type {announcement_type}")
                
                # Convert HTML content to markdown if available
                html_content = announcement.get("veriHtml", "")
                markdown_content = None
                if html_content:
                    try:
                        # Create BytesIO from HTML content
                        html_bytes = BytesIO(html_content.encode('utf-8'))
                        result = markitdown.convert_stream(html_bytes, file_extension=".html")
                        markdown_content = result.text_content if result else None
                    except Exception as e:
                        print(f"Warning: Failed to convert HTML to markdown in tender details: {e}")
                        markdown_content = None
                
                announcements.append({
                    "id": announcement.get("id"),
                    "type": {
                        "code": announcement_type,
                        "description": announcement_type_desc
                    },
                    "title": announcement.get("baslik"),
                    "date": announcement.get("ilanTarihi"),
                    "status": announcement.get("status"),
                    "html_content": html_content,
                    "markdown_content": markdown_content,
                    "content_preview": self._extract_text_preview(html_content)
                })
            
            # Build comprehensive response
            result = {
                "tender_id": item.get("id"),
                "ikn": item.get("ikn"),
                "name": item.get("ihaleAdi"),
                "status": {
                    "code": item.get("ihaleDurum"),
                    "description": basic_info.get("ihaleDurumAciklama")
                },
                "basic_info": {
                    "is_electronic": item.get("eIhale", False),
                    "method_code": item.get("ihaleUsul"),
                    "method_description": basic_info.get("ihaleUsulAciklama"),
                    "type_description": basic_info.get("ihaleTipiAciklama"),
                    "scope_description": item.get("ihaleKapsamAciklama"),
                    "tender_datetime": basic_info.get("ihaleTarihSaat"),
                    "location": basic_info.get("isinYapilacagiYer"),
                    "venue": basic_info.get("ihaleYeri"),
                    "complaint_fee": basic_info.get("itirazenSikayetBasvuruBedeli"),
                    "is_partial": item.get("kismiIhale", False)
                },
                "characteristics": characteristics,
                "okas_codes": okas_codes,
                "authority": authority_info,
                "process_rules": process_rules,
                "announcements_summary": {
                    "total_count": len(announcements),
                    "announcements": announcements,
                    "types_available": list(set(ann["type"]["description"] for ann in announcements))
                },
                "flags": {
                    "is_authority_tender": item.get("ihaleniIdaresiMi", False),
                    "is_without_announcement": item.get("ihaleIlansizMi", False),
                    "is_invitation_only": item.get("ihaleyeDavetEdilenMi", False),
                    "show_detail_documents": item.get("ihaleDetayDokumaniGorsunMu", False),
                    "show_document_downloaders": item.get("dokumanIndirenlerGosterilsinMi", False)
                },
                "document_count": item.get("dokumanSayisi", 0)
            }
            
            # Add cancellation info if tender is cancelled
            if basic_info.get("iptalTarihi"):
                result["cancellation_info"] = {
                    "cancelled_date": basic_info.get("iptalTarihi"),
                    "cancellation_reason": basic_info.get("iptalNedeni"),
                    "cancellation_article": basic_info.get("iptalMadde")
                }
            
            return result
            
        except httpx.HTTPStatusError as e:
            return {
                "error": f"API request failed with status {e.response.status_code}",
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": "Request failed - tender details",
                "message": str(e)
            }
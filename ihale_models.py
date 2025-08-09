#!/usr/bin/env python3
"""
Data models for Turkish Government Tenders (İhale) MCP Server
Contains all Pydantic models and static data for the EKAP v2 integration
"""

from typing import List
from pydantic import BaseModel, Field

# Data models for the API
class OkasCode(BaseModel):
    """OKAS (public procurement classification) code model"""
    code: str = Field(description="OKAS code")
    description: str = Field(description="Description of the OKAS code")
    category: str = Field(description="Category type (goods, services, etc.)")

class TenderType(BaseModel):
    """Tender type model"""
    id: int = Field(description="Tender type ID")
    code: str = Field(description="Tender type code")
    description: str = Field(description="Tender type description")

class TenderStatus(BaseModel):
    """Tender status model"""
    id: int = Field(description="Status ID")
    code: str = Field(description="Status code")
    description: str = Field(description="Status description")

class TenderMethod(BaseModel):
    """Tender method model"""
    code: str = Field(description="Method code")
    description: str = Field(description="Method description")

class Province(BaseModel):
    """Turkish province model"""
    name: str = Field(description="Province name")

class ProposalType(BaseModel):
    """Proposal/bid type model"""
    code: str = Field(description="Proposal type code")
    description: str = Field(description="Proposal type description")

class AnnouncementType(BaseModel):
    """Announcement type model"""
    code: str = Field(description="Announcement type code")  
    description: str = Field(description="Announcement type description")

class TenderDocument(BaseModel):
    """Tender document information"""
    id: int
    tender_id: int = Field(alias="ihaleId")
    date: str = Field(alias="tarih")

class TenderInfo(BaseModel):
    """Basic tender information from search results"""
    id: int
    name: str = Field(alias="ihaleAdi")
    type_code: str = Field(alias="ihaleTip")
    type_description: str = Field(alias="ihaleTipAciklama")
    ikn: str
    method_description: str = Field(alias="ihaleUsulAciklama")
    status_code: str = Field(alias="ihaleDurum")
    status_description: str = Field(alias="ihaleDurumAciklama")
    authority_name: str = Field(alias="idareAdi")
    province: str = Field(alias="ihaleIlAdi")
    tender_datetime: str = Field(alias="ihaleTarihSaat")
    is_followed: bool = Field(alias="takipEdiliyorMu")
    document_count: int = Field(alias="dokumanSayisi")
    documents: List[TenderDocument] = Field(alias="dokumanListe")
    has_announcement: bool = Field(alias="ilanVarMi")

class TenderSearchResponse(BaseModel):
    """Response from tender search API"""
    tenders: List[TenderInfo] = Field(alias="list")
    total_count: int = Field(alias="totalCount")

# Note: OKAS codes are now fetched dynamically from the live API via search_okas_codes tool
# The static list below is kept for reference but not used in the implementation

TENDER_TYPES = [
    TenderType(id=1, code="1", description="Mal (Goods/Equipment procurement)"),
    TenderType(id=2, code="2", description="Yapım (Construction/Infrastructure projects)"),
    TenderType(id=3, code="3", description="Hizmet (Services procurement)"),
    TenderType(id=4, code="4", description="Danışmanlık (Consultancy services)")
]

TENDER_STATUSES = [
    TenderStatus(id=1, code="1", description="İptal Edilmiş (Cancelled)"),
    TenderStatus(id=2, code="2", description="Teklifler Değerlendiriliyor (Bids under evaluation)"),
    TenderStatus(id=3, code="3", description="Teklif Vermeye Açık (Open for bidding)"),
    TenderStatus(id=4, code="4", description="Teklif Değerlendirme Tamamlanmış (Bid evaluation completed)"),
    TenderStatus(id=5, code="5", description="Sözleşme İmzalanmış (Contract signed)")
]

TENDER_METHODS = [
    TenderMethod(code="Açık", description="Açık İhale Usulü (Open tender method)"),
    TenderMethod(code="Belli İstekliler Arasında", description="Belli İstekliler Arasında İhale (Restricted tender)"),
    TenderMethod(code="Pazarlık", description="Pazarlık Usulü (Negotiated procedure)"),
    TenderMethod(code="Tasarım Yarışması", description="Tasarım Yarışması (Design competition)")
]

PROVINCES = [
    Province(name="ADANA"), Province(name="ADIYAMAN"), Province(name="AFYONKARAHİSAR"), Province(name="AĞRI"), 
    Province(name="AKSARAY"), Province(name="AMASYA"), Province(name="ANKARA"), Province(name="ANTALYA"), 
    Province(name="ARDAHAN"), Province(name="ARTVİN"), Province(name="AYDIN"), Province(name="BALIKESİR"),
    Province(name="BARTIN"), Province(name="BATMAN"), Province(name="BAYBURT"), Province(name="BİLECİK"), 
    Province(name="BİNGÖL"), Province(name="BİTLİS"), Province(name="BOLU"), Province(name="BURDUR"), 
    Province(name="BURSA"), Province(name="ÇANAKKALE"), Province(name="ÇANKIRI"), Province(name="ÇORUM"),
    Province(name="DENİZLİ"), Province(name="DİYARBAKIR"), Province(name="DÜZCE"), Province(name="EDİRNE"), 
    Province(name="ELAZIĞ"), Province(name="ERZİNCAN"), Province(name="ERZURUM"), Province(name="ESKİŞEHİR"), 
    Province(name="GAZİANTEP"), Province(name="GİRESUN"), Province(name="GÜMÜŞHANE"), Province(name="HAKKARİ"), 
    Province(name="HATAY"), Province(name="IĞDIR"), Province(name="ISPARTA"), Province(name="İSTANBUL"), 
    Province(name="İZMİR"), Province(name="KAHRAMANMARAŞ"), Province(name="KARABÜK"), Province(name="KARAMAN"), 
    Province(name="KARS"), Province(name="KASTAMONU"), Province(name="KAYSERİ"), Province(name="KIRIKKALE"), 
    Province(name="KIRKLARELI"), Province(name="KIRŞEHİR"), Province(name="KİLİS"), Province(name="KOCAELİ"), 
    Province(name="KONYA"), Province(name="KÜTAHYA"), Province(name="MALATYA"), Province(name="MANİSA"), 
    Province(name="MARDİN"), Province(name="MERSİN"), Province(name="MUĞLA"), Province(name="MUŞ"), 
    Province(name="NEVŞEHİR"), Province(name="NİĞDE"), Province(name="ORDU"), Province(name="OSMANİYE"), 
    Province(name="RİZE"), Province(name="SAKARYA"), Province(name="SAMSUN"), Province(name="SİİRT"), 
    Province(name="SİNOP"), Province(name="SİVAS"), Province(name="ŞANLIURFA"), Province(name="ŞIRNAK"), 
    Province(name="TEKİRDAĞ"), Province(name="TOKAT"), Province(name="TRABZON"), Province(name="TUNCELİ"), 
    Province(name="UŞAK"), Province(name="VAN"), Province(name="YALOVA"), Province(name="YOZGAT"), 
    Province(name="ZONGULDAK")
]

# Proposal Types - API expects numeric IDs
PROPOSAL_TYPES = {
    1: "Götürü-Anahtar Teslimi Götürü",
    2: "Birim Fiyat", 
    3: "Karma"
}

# Announcement Types - API expects numeric IDs
ANNOUNCEMENT_TYPES = {
    1: "Ön İlan",
    2: "İhale İlanı",
    3: "Sonuç İlanı",
    4: "İptal İlanı",
    5: "Ön Yeterlik İlanı",
    6: "Düzeltme İlanı"
}
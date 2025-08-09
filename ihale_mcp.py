#!/usr/bin/env python3
"""
MCP Server for Turkish Government Tenders (İhale)
Provides access to the Turkish government procurement portal EKAP v2
"""

from datetime import datetime, timedelta
from typing import List, Optional, Literal, Annotated, Dict, Any
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from ihale_client import EKAPClient
from ihale_models import (
    TENDER_TYPES, TENDER_STATUSES, TENDER_METHODS,
    PROVINCES, PROPOSAL_TYPES, ANNOUNCEMENT_TYPES,
    PLATE_TO_API_ID,
    TenderDocument, TenderInfo, TenderSearchResponse
)

# Initialize the MCP server and client
mcp = FastMCP(
    name="ihale-mcp",
    instructions="""
This server provides access to Turkish government tender (ihale) data from EKAP v2 portal.
Use the search_tenders tool to find tenders based on various criteria.
The server supports filtering by text, tender type, region, dates, and other parameters.
All tender information is in Turkish as it comes directly from the government portal.
"""
)

# Initialize EKAP API client
ekap_client = EKAPClient()



@mcp.tool
async def search_tenders(
    search_text: Annotated[str, "Text to search for in tender titles, descriptions, and specifications"] = "",
    ikn_year: Annotated[Optional[int], "IKN year (e.g., 2025)"] = None,
    ikn_number: Annotated[Optional[int], "IKN number"] = None,
    tender_types: Annotated[List[Literal[1, 2, 3, 4]], "Tender types: 1=Mal (Goods), 2=Yapım (Construction), 3=Hizmet (Service), 4=Danışmanlık (Consultancy)"] = None,
    tender_date_start: Annotated[Optional[str], "Start date for tender dates (YYYY-MM-DD format)"] = None,
    tender_date_end: Annotated[Optional[str], "End date for tender dates (YYYY-MM-DD format)"] = None,
    announcement_date_start: Annotated[Optional[str], "Start date for announcement dates (YYYY-MM-DD format)"] = None,
    announcement_date_end: Annotated[Optional[str], "End date for announcement dates (YYYY-MM-DD format)"] = None,
    announcement_date_filter: Annotated[Literal["today", "date_range"], "Announcement date filter type"] = None,
    tender_date_filter: Annotated[Literal["from_today", "date_range"], "Tender date filter type"] = None,
    search_type: Annotated[Literal["GirdigimGibi", "TumKelimeler"], "Search type: GirdigimGibi=exact match, TumKelimeler=all words"] = "GirdigimGibi",
    order_by: Annotated[Literal["ihaleTarihi", "ihaleAdi", "idareAdi"], "Order results by: ihaleTarihi=date, ihaleAdi=name, idareAdi=authority"] = "ihaleTarihi",
    sort_order: Annotated[Literal["asc", "desc"], "Sort order"] = "desc",
    # Boolean filters
    e_ihale: Annotated[Optional[bool], "Filter for electronic tenders (e-İhale)"] = None,
    e_eksiltme_yapilacak_mi: Annotated[Optional[bool], "Filter for electronic auctions (Elektronik eksiltme yapılacak mı)"] = None,
    ortak_alim_mi: Annotated[Optional[bool], "Filter for joint procurement (Ortak alım mı)"] = None,
    kismi_teklif_mi: Annotated[Optional[bool], "Filter for partial proposals (Kısmi teklif verilebilir mi)"] = None,
    fiyat_disi_unsur_varmi: Annotated[Optional[bool], "Filter for non-price factors (Fiyat dışı unsur var mı)"] = None,
    ekonomik_mali_yeterlilik_belgeleri_isteniyor_mu: Annotated[Optional[bool], "Filter for economic/financial qualification documents required"] = None,
    mesleki_teknik_yeterlilik_belgeleri_isteniyor_mu: Annotated[Optional[bool], "Filter for professional/technical qualification documents required"] = None,
    is_deneyimi_gosteren_belgeler_isteniyor_mu: Annotated[Optional[bool], "Filter for work experience documents required"] = None,
    yerli_istekliye_fiyat_avantaji_uygulanıyor_mu: Annotated[Optional[bool], "Filter for domestic bidder price advantage applied"] = None,
    yabanci_isteklilere_izin_veriliyor_mu: Annotated[Optional[bool], "Filter for foreign bidders allowed"] = None,
    alternatif_teklif_verilebilir_mi: Annotated[Optional[bool], "Filter for alternative proposals allowed"] = None,
    konsorsiyum_katilabilir_mi: Annotated[Optional[bool], "Filter for consortium participation allowed"] = None,
    alt_yuklenici_calistirilabilir_mi: Annotated[Optional[bool], "Filter for subcontractor employment allowed"] = None,
    fiyat_farki_verilecek_mi: Annotated[Optional[bool], "Filter for price difference to be given"] = None,
    avans_verilecek_mi: Annotated[Optional[bool], "Filter for advance payment to be given"] = None,
    cerceve_anlasmasi_mi: Annotated[Optional[bool], "Filter for framework agreements"] = None,
    personel_calistirilmasina_dayali_mi: Annotated[Optional[bool], "Filter for personnel employment based tenders"] = None,
    # List filters  
    provinces: Annotated[List[int], "Province plate numbers to filter by (1-81, e.g., 6=Ankara, 34=İstanbul, 35=İzmir)"] = None,
    tender_statuses: Annotated[List[int], "Tender status IDs to filter by"] = None,
    tender_methods: Annotated[List[int], "Tender method IDs to filter by"] = None,
    tender_sub_methods: Annotated[List[int], "Tender sub-method IDs to filter by"] = None,
    okas_codes: Annotated[List[str], "OKAS classification codes to filter by"] = None,
    authority_ids: Annotated[List[int], "Authority/institution IDs to filter by"] = None,
    proposal_types: Annotated[List[int], "Proposal type IDs: 1=Götürü-Anahtar Teslimi Götürü, 2=Birim Fiyat, 3=Karma"] = None,
    announcement_types: Annotated[List[int], "Announcement type IDs: 1=Ön İlan, 2=İhale İlanı, 3=Sonuç İlanı, etc."] = None,
    # Search scope parameters
    search_in_ikn: Annotated[bool, "Search in IKN (tender reference number)"] = True,
    search_in_title: Annotated[bool, "Search in tender title"] = True,
    search_in_announcement: Annotated[bool, "Search in tender announcement"] = True,
    search_in_tech_spec: Annotated[bool, "Search in technical specifications"] = True,
    search_in_admin_spec: Annotated[bool, "Search in administrative specifications"] = True,
    search_in_similar_work: Annotated[bool, "Search in similar work clause"] = True,
    search_in_location: Annotated[bool, "Search in work location clause"] = True,
    search_in_nature_quantity: Annotated[bool, "Search in nature/quantity clause"] = True,
    search_in_tender_info: Annotated[bool, "Search in tender information"] = True,
    search_in_contract_draft: Annotated[bool, "Search in contract draft"] = True,
    search_in_bid_form: Annotated[bool, "Search in bid form"] = True,
    limit: Annotated[int, "Maximum number of results to return (1-100)"] = 10,
    skip: Annotated[int, "Number of results to skip for pagination"] = 0
) -> Dict[str, Any]:
    """
    Search Turkish government tenders from EKAP v2 portal.
    
    Tender types: 1=Mal, 2=Yapım, 3=Hizmet, 4=Danışmanlık
    Provinces: Use plate numbers (6=Ankara, 34=İstanbul, 35=İzmir)
    IKN format: YEAR/NUMBER, dates: YYYY-MM-DD
    """
    
    # Validate limit
    if limit > 100:
        limit = 100
    elif limit < 1:
        limit = 1
    
    # Handle special date filters
    if announcement_date_filter == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        announcement_date_start = today
        announcement_date_end = today
    
    if tender_date_filter == "from_today":
        today = datetime.now().strftime("%Y-%m-%d")
        tender_date_start = today
        tender_date_end = None
    
    # Convert plate numbers to API IDs
    api_province_ids = None
    if provinces:
        api_province_ids = []
        for plate_number in provinces:
            api_id = PLATE_TO_API_ID.get(plate_number)
            if api_id:
                api_province_ids.append(api_id)
        # If no valid plate numbers, set to None to avoid empty filter
        if not api_province_ids:
            api_province_ids = None
    
    # Use the client to search tenders
    result = await ekap_client.search_tenders(
        search_text=search_text,
        ikn_year=ikn_year,
        ikn_number=ikn_number,
        tender_types=tender_types,
        tender_date_start=tender_date_start,
        tender_date_end=tender_date_end,
        announcement_date_start=announcement_date_start,
        announcement_date_end=announcement_date_end,
        search_type=search_type,
        order_by=order_by,
        sort_order=sort_order,
        # Boolean filters
        e_ihale=e_ihale,
        e_eksiltme_yapilacak_mi=e_eksiltme_yapilacak_mi,
        ortak_alim_mi=ortak_alim_mi,
        kismi_teklif_mi=kismi_teklif_mi,
        fiyat_disi_unsur_varmi=fiyat_disi_unsur_varmi,
        ekonomik_mali_yeterlilik_belgeleri_isteniyor_mu=ekonomik_mali_yeterlilik_belgeleri_isteniyor_mu,
        mesleki_teknik_yeterlilik_belgeleri_isteniyor_mu=mesleki_teknik_yeterlilik_belgeleri_isteniyor_mu,
        is_deneyimi_gosteren_belgeler_isteniyor_mu=is_deneyimi_gosteren_belgeler_isteniyor_mu,
        yerli_istekliye_fiyat_avantaji_uygulanıyor_mu=yerli_istekliye_fiyat_avantaji_uygulanıyor_mu,
        yabanci_isteklilere_izin_veriliyor_mu=yabanci_isteklilere_izin_veriliyor_mu,
        alternatif_teklif_verilebilir_mi=alternatif_teklif_verilebilir_mi,
        konsorsiyum_katilabilir_mi=konsorsiyum_katilabilir_mi,
        alt_yuklenici_calistirilabilir_mi=alt_yuklenici_calistirilabilir_mi,
        fiyat_farki_verilecek_mi=fiyat_farki_verilecek_mi,
        avans_verilecek_mi=avans_verilecek_mi,
        cerceve_anlasmasi_mi=cerceve_anlasmasi_mi,
        personel_calistirilmasina_dayali_mi=personel_calistirilmasina_dayali_mi,
        # List filters (provinces converted to API IDs)
        provinces=api_province_ids,
        tender_statuses=tender_statuses,
        tender_methods=tender_methods,
        tender_sub_methods=tender_sub_methods,
        okas_codes=okas_codes,
        authority_ids=authority_ids,
        proposal_types=proposal_types,
        announcement_types=announcement_types,
        # Search scope
        search_in_ikn=search_in_ikn,
        search_in_title=search_in_title,
        search_in_announcement=search_in_announcement,
        search_in_tech_spec=search_in_tech_spec,
        search_in_admin_spec=search_in_admin_spec,
        search_in_similar_work=search_in_similar_work,
        search_in_location=search_in_location,
        search_in_nature_quantity=search_in_nature_quantity,
        search_in_tender_info=search_in_tender_info,
        search_in_contract_draft=search_in_contract_draft,
        search_in_bid_form=search_in_bid_form,
        skip=skip,
        limit=limit
    )
    
    # Add search parameters to result for logging
    if "search_params" not in result:
        result["search_params"] = {
            "search_text": search_text,
            "ikn_year": ikn_year, 
            "ikn_number": ikn_number,
            "tender_types": tender_types,
            "date_range": {
                "tender_start": tender_date_start,
                "tender_end": tender_date_end,
                "announcement_start": announcement_date_start,
                "announcement_end": announcement_date_end
            }
        }
    
    return result


@mcp.tool
async def search_okas_codes(
    search_term: Annotated[str, "Search term to find matching OKAS codes by description"] = "",
    kalem_turu: Annotated[Optional[Literal[1, 2, 3]], "Filter by item type: 1=Mal (Goods), 2=Hizmet (Service), 3=Yapım (Construction)"] = None,
    limit: Annotated[int, "Maximum number of results to return (1-500)"] = 50
) -> Dict[str, Any]:
    """
    Search OKAS procurement classification codes.
    
    Item types: 1=Goods, 2=Service, 3=Construction
    Search in Turkish descriptions for best results.
    """
    
    # Use the client to search OKAS codes
    return await ekap_client.search_okas_codes(
        search_term=search_term,
        kalem_turu=kalem_turu,
        limit=limit
    )


@mcp.tool
async def search_authorities(
    search_term: Annotated[str, "Search term to find matching authorities/institutions by name"] = "",
    limit: Annotated[int, "Maximum number of results to return (1-500)"] = 50
) -> Dict[str, Any]:
    """
    Search Turkish government authorities/institutions.
    
    Find ministries, municipalities, universities for tender filtering.
    Search in Turkish for best results.
    """
    
    # Use the client to search authorities
    return await ekap_client.search_authorities(
        search_term=search_term,
        limit=limit
    )


@mcp.tool
async def get_recent_tenders(
    days: Annotated[int, "Number of days back to search (1-30)"] = 7,
    tender_types: Annotated[List[Literal[1, 2, 3, 4]], "Filter by tender types"] = None,
    limit: Annotated[int, "Maximum number of results (1-100)"] = 20
) -> Dict[str, Any]:
    """
    Get recent tenders from last N days.
    Convenience function for recent tender activity.
    """
    
    if days > 30:
        days = 30
    elif days < 1:
        days = 1
        
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Use the client to search for recent tenders
    result = await ekap_client.search_tenders(
        search_text="",
        tender_types=tender_types,
        announcement_date_start=start_date_str,
        announcement_date_end=end_date_str,
        order_by="ihaleTarihi",
        sort_order="desc",
        limit=limit
    )
    
    if result.get("error"):
        return result
        
    return {
        "recent_tenders": result.get("tenders", []),
        "total_count": result.get("total_count", 0),
        "date_range": {
            "start": start_date_str,
            "end": end_date_str,
            "days_back": days
        },
        "filters_applied": {
            "tender_types": tender_types,
            "limit": limit
        }
    }


@mcp.tool
async def get_tender_announcements(
    tender_id: Annotated[int, "The tender ID to get announcements for"]
) -> Dict[str, Any]:
    """
    Get all announcements for a tender with HTML-to-Markdown conversion.
    
    Returns: Ön İlan, İhale İlanı, Sonuç İlanı, İptal İlanı, etc.
    """
    
    # Use the client to get tender announcements (always converts to markdown)
    result = await ekap_client.get_tender_announcements(tender_id)
    
    if result.get("error"):
        return result
    
    # Format the response
    announcements = result.get("announcements", [])
    
    return {
        "announcements": announcements,
        "total_announcements": result.get("total_count", 0),
        "tender_id": tender_id,
        "announcement_types_found": list(set(ann.get("type", {}).get("description", "Unknown") for ann in announcements))
    }


@mcp.tool
async def get_tender_details(
    tender_id: Annotated[int, "The tender ID to get comprehensive details for"]
) -> Dict[str, Any]:
    """
    Get comprehensive tender details with HTML-to-Markdown conversion.
    
    Returns: basic info, characteristics, OKAS codes, authority details, 
    process rules, announcements summary, cancellation info if applicable.
    """
    
    # Use the client to get tender details
    result = await ekap_client.get_tender_details(tender_id)
    
    if result.get("error"):
        return result
    
    return {
        "tender_details": result,
        "summary": {
            "tender_name": result.get("name"),
            "ikn": result.get("ikn"),
            "status": result.get("status", {}).get("description"),
            "authority": result.get("authority", {}).get("name"),
            "location": result.get("basic_info", {}).get("location"),
            "is_electronic": result.get("basic_info", {}).get("is_electronic"),
            "characteristics_count": len(result.get("characteristics", [])),
            "okas_codes_count": len(result.get("okas_codes", [])),
            "announcements_count": result.get("announcements_summary", {}).get("total_count", 0)
        }
    }



def main():
    """Main entry point for the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()
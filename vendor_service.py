import logging
from typing import List, Dict, Any

class VendorService:
    """Service class for managing vendor data and operations"""
    
    def __init__(self):
        """Initialize vendor service with in-memory vendor database"""
        self.vendors_db = self._initialize_vendors_db()
        
    def _initialize_vendors_db(self) -> List[Dict[str, Any]]:
        """Initialize in-memory vendor database with realistic procurement data"""
        return [
            # Coal and Mining Equipment suppliers
            {
                'vendor_id': 'COAL001',
                'name': 'Advanced Coal Handling Systems',
                'materials_supplied': ['coal handling equipment', 'conveyor belts', 'mining machinery parts'],
                'quality_rating': 9.3,
                'quantity_available': 25000,
                'price_per_unit': 15000.00,
                'delivery_time': 21,
                'location': 'Kolkata, West Bengal',
                'certifications': ['ISO 9001', 'Coal India Limited Approved'],
                'contact_info': 'sales@coalhandling.in'
            },
            {
                'vendor_id': 'MINING001',
                'name': 'Bharat Mining Equipment Ltd',
                'materials_supplied': ['rock drilling equipment', 'excavator parts', 'safety equipment'],
                'quality_rating': 8.9,
                'quantity_available': 15000,
                'price_per_unit': 25000.00,
                'delivery_time': 28,
                'location': 'Chennai, Tamil Nadu',
                'certifications': ['IS 2062', 'DGMS Approved'],
                'contact_info': 'procurement@bharatmining.com'
            },
            
            # Power Generation Equipment suppliers
            {
                'vendor_id': 'POWER001',
                'name': 'Thermal Power Components India',
                'materials_supplied': ['boiler tubes', 'turbine components', 'generator parts'],
                'quality_rating': 9.5,
                'quantity_available': 8000,
                'price_per_unit': 45000.00,
                'delivery_time': 35,
                'location': 'Trichy, Tamil Nadu',
                'certifications': ['ASME', 'NTPC Approved', 'ISO 9001'],
                'contact_info': 'orders@thermalpower.in'
            },
            {
                'vendor_id': 'ELEC001',
                'name': 'National Electrical Systems',
                'materials_supplied': ['electrical cables', 'control systems', 'transformer equipment'],
                'quality_rating': 9.1,
                'quantity_available': 12000,
                'price_per_unit': 8500.00,
                'delivery_time': 18,
                'location': 'Neyveli, Tamil Nadu',
                'certifications': ['BIS', 'CEA Approved', 'ISO 9001'],
                'contact_info': 'sales@nationalelectrical.in'
            },
            
            # Steel suppliers
            {
                'vendor_id': 'STEEL001',
                'name': 'Premium Steel Corporation',
                'materials_supplied': ['steel', 'stainless steel', 'carbon steel', 'structural steel'],
                'quality_rating': 9.2,
                'quantity_available': 50000,
                'price_per_unit': 1250.00,
                'delivery_time': 14,
                'location': 'Pittsburgh, PA',
                'certifications': ['ISO 9001', 'ASTM A36'],
                'contact_info': 'orders@premiumsteel.com'
            },
            {
                'vendor_id': 'STEEL002',
                'name': 'Industrial Steel Solutions',
                'materials_supplied': ['steel', 'alloy steel', 'structural steel'],
                'quality_rating': 8.7,
                'quantity_available': 75000,
                'price_per_unit': 1180.00,
                'delivery_time': 10,
                'location': 'Gary, IN',
                'certifications': ['ISO 9001', 'ASTM A992'],
                'contact_info': 'sales@industrialsteel.com'
            },
            {
                'vendor_id': 'STEEL003',
                'name': 'Global Steel Suppliers',
                'materials_supplied': ['steel', 'galvanized steel', 'tool steel'],
                'quality_rating': 8.1,
                'quantity_available': 100000,
                'price_per_unit': 1100.00,
                'delivery_time': 21,
                'location': 'Birmingham, AL',
                'certifications': ['ISO 9001'],
                'contact_info': 'procurement@globalsteel.com'
            },
            
            # Aluminum suppliers
            {
                'vendor_id': 'ALU001',
                'name': 'Apex Aluminum Industries',
                'materials_supplied': ['aluminum', 'aluminum alloy', 'aluminum sheet'],
                'quality_rating': 9.1,
                'quantity_available': 30000,
                'price_per_unit': 2100.00,
                'delivery_time': 12,
                'location': 'Seattle, WA',
                'certifications': ['ISO 9001', 'AS9100'],
                'contact_info': 'orders@apexaluminum.com'
            },
            {
                'vendor_id': 'ALU002',
                'name': 'Pacific Aluminum Corp',
                'materials_supplied': ['aluminum', 'marine grade aluminum'],
                'quality_rating': 8.9,
                'quantity_available': 40000,
                'price_per_unit': 1950.00,
                'delivery_time': 8,
                'location': 'Los Angeles, CA',
                'certifications': ['ISO 9001', 'ASTM B209'],
                'contact_info': 'sales@pacificaluminum.com'
            },
            {
                'vendor_id': 'ALU003',
                'name': 'Continental Aluminum Supply',
                'materials_supplied': ['aluminum', 'extruded aluminum', 'aluminum plate'],
                'quality_rating': 8.3,
                'quantity_available': 60000,
                'price_per_unit': 1850.00,
                'delivery_time': 18,
                'location': 'Phoenix, AZ',
                'certifications': ['ISO 9001'],
                'contact_info': 'info@contialuminum.com'
            },
            
            # Copper suppliers
            {
                'vendor_id': 'COP001',
                'name': 'Premier Copper Works',
                'materials_supplied': ['copper', 'copper wire', 'copper pipe'],
                'quality_rating': 9.4,
                'quantity_available': 25000,
                'price_per_unit': 8500.00,
                'delivery_time': 7,
                'location': 'Denver, CO',
                'certifications': ['ISO 9001', 'ASTM B88'],
                'contact_info': 'orders@premiercopper.com'
            },
            {
                'vendor_id': 'COP002',
                'name': 'Mountain State Copper',
                'materials_supplied': ['copper', 'brass', 'bronze'],
                'quality_rating': 8.8,
                'quantity_available': 35000,
                'price_per_unit': 8200.00,
                'delivery_time': 15,
                'location': 'Salt Lake City, UT',
                'certifications': ['ISO 9001', 'ASTM B280'],
                'contact_info': 'sales@mountaincopper.com'
            },
            
            # Plastic suppliers
            {
                'vendor_id': 'PLAS001',
                'name': 'Advanced Polymer Solutions',
                'materials_supplied': ['plastic', 'polymer', 'engineering plastic'],
                'quality_rating': 8.9,
                'quantity_available': 80000,
                'price_per_unit': 450.00,
                'delivery_time': 5,
                'location': 'Houston, TX',
                'certifications': ['ISO 9001', 'FDA Approved'],
                'contact_info': 'orders@advancedpolymer.com'
            },
            {
                'vendor_id': 'PLAS002',
                'name': 'Industrial Plastics Inc',
                'materials_supplied': ['plastic', 'recycled plastic', 'plastic sheet'],
                'quality_rating': 8.2,
                'quantity_available': 120000,
                'price_per_unit': 380.00,
                'delivery_time': 12,
                'location': 'Detroit, MI',
                'certifications': ['ISO 9001', 'Green Certified'],
                'contact_info': 'procurement@indplastics.com'
            },
            
            # Rubber suppliers
            {
                'vendor_id': 'RUB001',
                'name': 'Elite Rubber Manufacturing',
                'materials_supplied': ['rubber', 'synthetic rubber', 'natural rubber'],
                'quality_rating': 8.7,
                'quantity_available': 45000,
                'price_per_unit': 1200.00,
                'delivery_time': 10,
                'location': 'Akron, OH',
                'certifications': ['ISO 9001', 'ASTM D2000'],
                'contact_info': 'sales@eliterubber.com'
            },
            
            # Heavy Machinery and Construction suppliers
            {
                'vendor_id': 'HEAVY001',
                'name': 'Indian Heavy Engineering Corp',
                'materials_supplied': ['heavy machinery', 'construction equipment', 'maintenance supplies'],
                'quality_rating': 8.8,
                'quantity_available': 5000,
                'price_per_unit': 150000.00,
                'delivery_time': 45,
                'location': 'Ranchi, Jharkhand',
                'certifications': ['ISO 9001', 'CII Approved'],
                'contact_info': 'sales@ihec.in'
            },
            {
                'vendor_id': 'CONST001',
                'name': 'Tamil Nadu Construction Materials',
                'materials_supplied': ['concrete materials', 'cement', 'construction tools'],
                'quality_rating': 8.4,
                'quantity_available': 100000,
                'price_per_unit': 850.00,
                'delivery_time': 12,
                'location': 'Coimbatore, Tamil Nadu',
                'certifications': ['BIS', 'Quality Council of India'],
                'contact_info': 'orders@tnconst.com'
            },
            {
                'vendor_id': 'WELD001',
                'name': 'Advanced Welding Solutions India',
                'materials_supplied': ['welding materials', 'welding equipment', 'safety equipment'],
                'quality_rating': 8.7,
                'quantity_available': 20000,
                'price_per_unit': 2500.00,
                'delivery_time': 15,
                'location': 'Puducherry',
                'certifications': ['AWS', 'IS 814', 'ISO 9001'],
                'contact_info': 'procurement@advancedwelding.in'
            },
            
            # Textile suppliers (keeping some for completeness)
            {
                'vendor_id': 'TEX001',
                'name': 'Superior Textile Mills',
                'materials_supplied': ['textile', 'cotton', 'synthetic fiber'],
                'quality_rating': 8.5,
                'quantity_available': 200000,
                'price_per_unit': 85.00,
                'delivery_time': 6,
                'location': 'Charlotte, NC',
                'certifications': ['OEKO-TEX', 'GOTS'],
                'contact_info': 'orders@supertextile.com'
            }
        ]
    
    def get_all_vendors(self) -> List[Dict[str, Any]]:
        """Get all vendors from the database"""
        return self.vendors_db.copy()
    
    def get_vendors_by_material(self, material_type: str) -> List[Dict[str, Any]]:
        """
        Get vendors that supply a specific material type
        
        Args:
            material_type: The type of material to search for
            
        Returns:
            List of vendor dictionaries that supply the material
        """
        material_type_lower = material_type.lower().strip()
        matching_vendors = []
        
        for vendor in self.vendors_db:
            # Check if any of the vendor's materials match the requested type
            for material in vendor['materials_supplied']:
                if material_type_lower in material.lower():
                    matching_vendors.append(vendor.copy())
                    break
        
        logging.info(f"Found {len(matching_vendors)} vendors for material type: {material_type}")
        return matching_vendors
    
    def get_vendor_by_id(self, vendor_id: str) -> Dict[str, Any]:
        """
        Get a specific vendor by their ID
        
        Args:
            vendor_id: The unique identifier for the vendor
            
        Returns:
            Vendor dictionary or None if not found
        """
        for vendor in self.vendors_db:
            if vendor['vendor_id'] == vendor_id:
                return vendor.copy()
        return None
    
    def get_available_materials(self) -> List[str]:
        """
        Get a list of all available material types
        
        Returns:
            Sorted list of unique material types
        """
        materials = set()
        for vendor in self.vendors_db:
            materials.update(vendor['materials_supplied'])
        
        return sorted(list(materials))
    
    def filter_vendors_by_criteria(self, vendors: List[Dict[str, Any]], 
                                 min_quality: float = 0.0,
                                 min_quantity: float = 0.0,
                                 max_price: float = float('inf'),
                                 max_delivery_time: int = 365) -> List[Dict[str, Any]]:
        """
        Filter vendors based on specific criteria
        
        Args:
            vendors: List of vendor dictionaries to filter
            min_quality: Minimum quality rating required
            min_quantity: Minimum quantity available required
            max_price: Maximum price per unit allowed
            max_delivery_time: Maximum delivery time in days allowed
            
        Returns:
            Filtered list of vendors
        """
        filtered_vendors = []
        
        for vendor in vendors:
            if (vendor['quality_rating'] >= min_quality and
                vendor['quantity_available'] >= min_quantity and
                vendor['price_per_unit'] <= max_price and
                vendor['delivery_time'] <= max_delivery_time):
                filtered_vendors.append(vendor)
        
        logging.info(f"Filtered {len(filtered_vendors)} vendors from {len(vendors)} based on criteria")
        return filtered_vendors

# Changelog - GST Billing Software

All notable changes and releases for **GST Billing Software** are documented here.

---

## [2.0.0] - 2026-11-04

### Architecture Overhaul
- **High-Performance FastAPI Backend**:
  - Re-architected backend to Python FastAPI 0.115 with high-throughput asynchronous request processing.
  - Implemented 20 dedicated modular routers for clean separation of concerns.
  - Added native Pydantic schemas with automatic OpenAPI (Swagger) documentation.
  - Added atomic JSON storage engine with in-memory caching and safe transaction rollbacks.
  - Implemented Scrypt PIN hashing with rate limiting and emergency reset capability.
  - Implemented sensitive financial data and PII redaction across all system logs.
  - Added transactional backup snapshots and automated daily rotation.
  - Added native PostgreSQL integration with real-time dual-write synchronization.
  - Added MCA Rule 3 compliant unalterable Audit Trail (`audit_logs`) and CSV export.

- **Modern React 19 Frontend**:
  - Upgraded frontend to React 19 + Vite 7 with modular component architecture in `frontend/`.
  - Full offline PWA capabilities with service worker caching.
  - Client-side Tesseract.js OCR engine for receipt and document processing.
  - Modern responsive dark/light UI theme with real-time GST calculations.

- **Compliance & GST Capabilities**:
  - Real-time CGST, SGST, IGST, UTGST, and Cess calculations with inter-state detection.
  - TDS (Form 26Q) and TCS (Form 27EQ) deductions and ledger reports.
  - Multi-currency support across 22 global currencies with live FX conversions.
  - GSTR-1, GSTR-3B JSON exports and GSTR-2B reconciliation.
  - NIC-compliant e-Way bill and e-Invoicing JSON generation.
  - Bill of Supply, Delivery Challan, Proforma, Credit & Debit Note generation.

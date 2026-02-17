# In tis setion we are providing the ML code and some good research papers.

## AI assistant architecture note
- See `AI_AGENT_SYSTEM_DESIGN.md` for a complete system design for building a conversational AI agent over invoicing and inventory SQLite data.

## Runnable Python demo (with sample SQLite data)
- File: `business_ai_assistant.py`
- It creates a sample multi-tenant invoicing + inventory database and provides a safe business Q&A assistant.

### Quick start
```bash
python business_ai_assistant.py --init-db
python business_ai_assistant.py --tenant 1 --ask "What was my total sales last month?"
python business_ai_assistant.py --tenant 1 --ask "Who are my top 10 customers by revenue?"
python business_ai_assistant.py --tenant 1 --ask "Which products are low stock?"
python business_ai_assistant.py --tenant 1 --chat
```

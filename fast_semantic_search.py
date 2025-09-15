def _search_top_tables(self, question: str):
        q_emb = self.model.encode(
            question, convert_to_tensor=True, normalize_embeddings=self.normalize
        )
        scores = util.cos_sim(q_emb, self.table_embeddings).detach().cpu().numpy().ravel()
        top_idx = np.argsort(-scores)[: self.top_k]
        top_tables = [self.table_names[i] for i in top_idx]
        top_scores = [float(scores[i]) for i in top_idx]
        return top_tables, top_scores

def answer_question(self, question: str):
    top_tables, top_scores = self._search_top_tables(question)
    results = []
    for t, sc in zip(top_tables, top_scores):
        results.append({

            "ddl": self.table_ddls.get(t, None)
        })
    return results

# ================= FastAPI =================

app = FastAPI(
    title="Schema Semantic Search API",
    description="API orqali SQL schema faylidagi top 30 jadvalni semantic search yordamida topish va DDL qaytarish",
    version="1.0.0"
)

class TableResult(BaseModel):
    ddl: str | None

class QuestionRequest(BaseModel):
    question: str

class SearchResponse(BaseModel):
    question: str
    top_tables: List[TableResult]

# Global searcher
searcher = SchemaSemanticSearch(
    schema_file=r"/home/tensor/coding/vscode/sqlcoder/ddl.sql",
    model_id="sentence-transformers/LaBSE",
    hf_cache=r"/home/tensor/coding/vscode/sqlcoder/hf_cache",
)

@app.post("/search", response_model=SearchResponse, summary="Search top 30 tables by question")
def search_schema(request: QuestionRequest):
    """
    Savolni qabul qiladi va schema faylidagi eng mos keladigan 30 ta jadval va ularning DDL larini qaytaradi.
    
    ### Request body:
    - `question` : string
    
    ### Response:
    - `question` : yuborilgan savol
    - `top_tables` : ro'yxat (table, score, ddl)
    """
    results = searcher.answer_question(request.question)
    print(request.question)
    return SearchResponse(question=request.question, top_tables=results)
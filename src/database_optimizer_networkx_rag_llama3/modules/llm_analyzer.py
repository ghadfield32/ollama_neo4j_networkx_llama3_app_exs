from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage

class FlexibleDatabaseLLM:
    def __init__(self, graph, debug=False):
        self.graph = graph
        self.llm = ChatOllama(model="llama3.2")
        self.debug = debug

    def extract_table_info(self):
        table_info = {}
        for node, attrs in self.graph.nodes(data=True):
            if attrs['type'] == 'table':
                table_info[node] = {'columns': [], 'db': attrs['db']}
        for node, attrs in self.graph.nodes(data=True):
            if attrs['type'] == 'column':
                table_name = node.split('.')[0] + '.' + node.split('.')[1]
                if table_name in table_info:
                    table_info[table_name]['columns'].append(attrs['label'])
        if self.debug:
            print("Extracted table info:", table_info)
        return table_info

    def query_schema_with_prompt(self, custom_prompt):
        table_info = self.extract_table_info()
        table_details = "\n".join([f"Table {key} has columns: {', '.join(value['columns'])}" for key, value in table_info.items()])
        prompt_content = f"{custom_prompt}\n\n{table_details}"
        message = HumanMessage(content=prompt_content)
        response = self.llm([message])
        if self.debug:
            print(f"\nLLM Analysis:\n{response.content}")
        return response.content

def main(debug=False):
    _, _, metadata1, metadata2 = setup_databases(debug)
    graph = construct_graph(metadata1, metadata2, debug=debug)
    llm_analyzer = FlexibleDatabaseLLM(graph, debug=debug)
    prompt = "Identify any tables that appear to be duplicates or serve similar purposes."
    response = llm_analyzer.query_schema_with_prompt(prompt)
    print(response)

if __name__ == "__main__":
    main(debug=True)

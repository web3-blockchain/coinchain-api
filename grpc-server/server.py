from concurrent import futures
import grpc
import news_pb2
import news_pb2_grpc

class NewsService(news_pb2_grpc.NewsServiceServicer):
    def FetchNews(self, request, context):
        news_links = fetch_news_links(url)
        news_items = [news_pb2.NewsItem(text=news['text'], url=news['url']) for news in news_links]
        return news_pb2.NewsResponse(news_items=news_items)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    news_pb2_grpc.add_NewsServiceServicer_to_server(NewsService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()

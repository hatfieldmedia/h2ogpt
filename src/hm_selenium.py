import logging
import langchain.document_loaders
from typing import TYPE_CHECKING, List, Literal, Optional, Union

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

logger = logging.getLogger(__name__)

class SeleniumURLLoader(langchain.document_loaders.SeleniumURLLoader):
  
  def load(self) -> List[Document]:
    """Load the specified URLs using Selenium and create Document instances.

    Returns:
      List[Document]: A list of Document instances with loaded content.
    """
    from unstructured.partition.html import partition_html

    docs: List[Document] = list()
    driver = self._get_driver()
    driver.set_script_timeout(30)
    for url in self.urls:
      try:
        driver.get(url)
        text = driver.execute_async_script("""
          const done = arguments[arguments.length - 1];
          const readability = async () => {
            const atf = document.getElementsByClassName('above-the-fold');
            const app = document.getElementById('app')
            Array.from(atf).reverse().forEach(el => {
              app.insertBefore(el, app.firstChild);
            })
            
            const r = await import('https://cdn.skypack.dev/@mozilla/readability');
            const d = document.cloneNode(true)
            return (new r.Readability(d, {debug: true, nbTopCandidates: 10})).parse();
          }
                    
          let r = await readability()
          done(r.textContent)
        """)
        # logger.error(text)
        # page_content = driver.page_source // originally this
        # elements = partition_html(text=page_content)
        # text = "\n\n".join([str(el) for el in elements])
        metadata = {"source": url}
        docs.append(Document(page_content=text, metadata=metadata))
      except Exception as e:
        if self.continue_on_failure:
          logger.error(f"Error fetching or processing {url}, exception: {e}")
        else:
          raise e

    driver.quit()
    return docs

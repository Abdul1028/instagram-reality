import streamlit as st
from typing import List
from streamlit.components.v1 import ComponentBase

class AppendTextArea(ComponentBase):
    def __init__(self, key=None):
        super().__init__(key=key)

    def _get_value(self, value):
        self.value = value

    def _get_script(self):
        return """
        <script>
        const componentId = document.currentScript.getAttribute('componentId');

        function appendValue(value) {
            const component = document.querySelector(`#${componentId}`);
            component.value = value;
            const event = new Event('change');
            component.dispatchEvent(event);
        }

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && event.target.tagName === 'TEXTAREA') {
                event.preventDefault();
                const enteredValue = event.target.value.trim();
                if (enteredValue !== '') {
                    appendValue(enteredValue);
                    event.target.value = '';
                }
            }
        });
        </script>
        """

    def _repr_html_(self):
        return f"""
        <textarea id="{self.get_id()}" style="width: 100%; height: 200px;"></textarea>
        {self._get_script()}
        """

def append_text_area() -> List[str]:
    return st.component(AppendTextArea, "")

if __name__ == "__main__":
    entered_values = append_text_area()
    st.write("Entered Values:", entered_values)

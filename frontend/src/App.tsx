import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';
import Api from './services/Api';

const App = () =>  {
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("Loading...");
  useEffect(() => {
    Api.post("count", {
      query: "victoria"
    }).then((res) => {
      setText(res);
      setLoading(false);
    })
  }, []);
  return (
    <div className="App">
      <header className="App-header">
        {text}
      </header>
    </div>
  );
}

export default App;

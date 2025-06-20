import React, { useState } from 'react';
import './App.css';
import Header from "./MyComponents/Header";
import { Todos } from "./MyComponents/Todos";
import { Footer } from "./MyComponents/Footer";
import { AddTodo } from "./MyComponents/AddTodo";
import { About } from "./MyComponents/About";
import {
  BrowserRouter as Router,
  Routes,
  Route
} from "react-router-dom";

function App() {
  const [todos, setTodos] = useState([]);

  const addTodo = (title, desc) => {
    const sno = todos.length === 0 ? 1 : todos[todos.length - 1].sno + 1;
    const newTodo = {
      sno: sno,
      title: title,
      desc: desc
    };
    setTodos([...todos, newTodo]);
  };

  const onDelete = (todo) => {
    setTodos(todos.filter((e) => e !== todo));
  };

  return (
    <Router>
      <Header title="My Todos List" searchBar={false} />
      <Routes>
        <Route
          path="/"
          element={
            <>
              <AddTodo addTodo={addTodo} />
              <Todos todos={todos} onDelete={onDelete} />
            </>
          }
        />
        <Route path="/about" element={<About />} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;

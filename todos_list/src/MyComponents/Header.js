import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

export default function Header(props) {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <div className="container-fluid">
        <div className="navbar-brand d-flex align-items-center">
          <img src="/todo_app.svg" alt="Todo App Logo" className="navbar-logo" />
          <Link className="navbar-brand-text" to="/">{props.title}</Link>
        </div>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <Link className="nav-link active" to="/">Home</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/about">About</Link>
            </li>
          </ul>
          {props.searchBar ? (
            <form className="d-flex" role="search">
              <input className="form-control me-2" type="search" placeholder="Search" aria-label="Search" />
              <button className="btn btn-outline-success" type="submit">Search</button>
            </form>
          ) : null}
        </div>
      </div>
    </nav>
  );
}

Header.defaultProps = {
  title: "Your Title Here",
  searchBar: true
};

Header.propTypes = {
  title: PropTypes.string,
  searchBar: PropTypes.bool.isRequired
};
import React from 'react'

export const Footer = () => {

    let footerStyle = {
        position: "absolute",
        top: "100vh",
        width: "100%",
        border: "2px solid red"
    }
    return (
        <div>
            <div className='bg-dark text-light py-3' style={footerStyle}>
                <p className='text-center'>
                    Copyright &copy; MyTodosList.com
                </p>
            </div>

        </div>
    )
}

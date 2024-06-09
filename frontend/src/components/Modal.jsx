import React from 'react'
import Modal from 'react-modal'

const customModalStyles = {
    content: {
        width: '90%',
        margin: 'auto',
    },

};

const ModalComponent = ({isOpen, closeModal, content}) => {
    return (
        <Modal
        isOpen={isOpen}
        onRequestClose={closeModal}
        contentLabel='Modal'
        style={customModalStyles}
        >
            {content}
        </Modal>
    );
};

export default ModalComponent;
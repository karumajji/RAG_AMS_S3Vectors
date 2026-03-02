#!/usr/bin/env python3
"""
Generate Fake Documents and Embeddings for RAG System Testing

This script:
1. Generates 50 fake documents with varied content across different topics
2. Creates 1024-dimensional vector embeddings using Amazon Titan Text Embeddings V2
3. Saves documents and embeddings to files

Topics covered:
- Technology
- Science
- Business
- Health
- Education

Prerequisites:
- AWS credentials configured
- Access to Amazon Bedrock with Titan Text Embeddings V2
"""

import json
import numpy as np
import boto3
import time
from datetime import datetime

# Document templates by topic
TECHNOLOGY_DOCS = [
    {
        "title": "Introduction to Machine Learning",
        "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves. The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future."
    },
    {
        "title": "Cloud Computing Fundamentals",
        "content": "Cloud computing is the delivery of computing services including servers, storage, databases, networking, software, analytics, and intelligence over the Internet to offer faster innovation, flexible resources, and economies of scale. You typically pay only for cloud services you use, helping lower operating costs, run infrastructure more efficiently, and scale as business needs change."
    },
    {
        "title": "Cybersecurity Best Practices",
        "content": "Cybersecurity involves protecting systems, networks, and programs from digital attacks. These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information, extorting money from users, or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people, and attackers are becoming more innovative."
    },
    {
        "title": "Blockchain Technology Overview",
        "content": "Blockchain is a distributed database or ledger that is shared among the nodes of a computer network. As a database, a blockchain stores information electronically in digital format. Blockchains are best known for their crucial role in cryptocurrency systems for maintaining a secure and decentralized record of transactions. The innovation with a blockchain is that it guarantees the fidelity and security of a record of data."
    },
    {
        "title": "Internet of Things Applications",
        "content": "The Internet of Things describes the network of physical objects that are embedded with sensors, software, and other technologies for the purpose of connecting and exchanging data with other devices and systems over the internet. These devices range from ordinary household objects to sophisticated industrial tools. IoT enables devices to communicate with each other and with centralized systems, creating opportunities for more direct integration of the physical world into computer-based systems."
    },
    {
        "title": "Artificial Intelligence Ethics",
        "content": "AI ethics is a set of values, principles, and techniques that employ widely accepted standards of right and wrong to guide moral conduct in the development and use of AI technologies. As AI systems become more prevalent and powerful, questions about their ethical implications become increasingly important. Key concerns include bias in AI algorithms, privacy issues, transparency, accountability, and the potential impact on employment."
    },
    {
        "title": "Quantum Computing Basics",
        "content": "Quantum computing is a type of computation that harnesses the collective properties of quantum states, such as superposition, interference, and entanglement, to perform calculations. The devices that perform quantum computations are known as quantum computers. Quantum computers are believed to be able to solve certain computational problems, such as integer factorization, substantially faster than classical computers."
    },
    {
        "title": "5G Network Technology",
        "content": "5G is the fifth generation technology standard for broadband cellular networks. 5G networks are predicted to have more than 1.7 billion subscribers worldwide by 2025. The main advantage of the new networks is that they will have greater bandwidth, giving higher download speeds, eventually up to 10 gigabits per second. Due to the increased bandwidth, it is expected the networks will increasingly be used as general internet service providers for laptops and desktop computers."
    },
    {
        "title": "DevOps Methodology",
        "content": "DevOps is a set of practices that combines software development and IT operations. It aims to shorten the systems development life cycle and provide continuous delivery with high software quality. DevOps is complementary with Agile software development; several DevOps aspects came from the Agile methodology. The DevOps movement began around 2007 when the software development and IT operations communities raised concerns about the traditional software development model."
    },
    {
        "title": "Edge Computing Explained",
        "content": "Edge computing is a distributed computing paradigm that brings computation and data storage closer to the sources of data. This is expected to improve response times and save bandwidth. Edge computing is an architecture rather than a specific technology, and a topology- and location-sensitive form of distributed computing. The origins of edge computing lie in content delivery networks that were created in the late 1990s to serve web and video content from edge servers."
    }
]

SCIENCE_DOCS = [
    {
        "title": "Climate Change and Global Warming",
        "content": "Climate change refers to long-term shifts in temperatures and weather patterns. These shifts may be natural, but since the 1800s, human activities have been the main driver of climate change, primarily due to the burning of fossil fuels like coal, oil, and gas. Burning fossil fuels generates greenhouse gas emissions that act like a blanket wrapped around the Earth, trapping the sun's heat and raising temperatures."
    },
    {
        "title": "DNA and Genetic Engineering",
        "content": "Genetic engineering is the process of using recombinant DNA technology to alter the genetic makeup of an organism. Traditionally, humans have manipulated genomes indirectly by controlling breeding and selecting offspring with desired traits. Genetic engineering involves the direct manipulation of one or more genes. Most often, a gene from another species is added to an organism's genome to give it a desired phenotype."
    },
    {
        "title": "Renewable Energy Sources",
        "content": "Renewable energy is energy that is collected from renewable resources that are naturally replenished on a human timescale. It includes sources such as sunlight, wind, rain, tides, waves, and geothermal heat. Renewable energy stands in contrast to fossil fuels, which are being used far more quickly than they are being replenished. Although most renewable energy sources are sustainable, some are not."
    },
    {
        "title": "The Human Brain Structure",
        "content": "The human brain is the central organ of the human nervous system, and with the spinal cord makes up the central nervous system. The brain consists of the cerebrum, the brainstem and the cerebellum. It controls most of the activities of the body, processing, integrating, and coordinating the information it receives from the sense organs, and making decisions as to the instructions sent to the rest of the body."
    },
    {
        "title": "Particle Physics Fundamentals",
        "content": "Particle physics is a branch of physics that studies the nature of the particles that constitute matter and radiation. The field also studies combinations of elementary particles up to the scale of protons and neutrons, while the study of combination of protons and neutrons is called nuclear physics. The fundamental particles in the universe are classified in the Standard Model as fermions and bosons."
    },
    {
        "title": "Ocean Ecosystems",
        "content": "Marine ecosystems are aquatic environments with high levels of dissolved salt. These include the open ocean, the deep-sea ocean, and coastal marine ecosystems, each of which have different physical and biological characteristics. Marine ecosystems are the largest of Earth's aquatic ecosystems and are distinguished by waters that have a high salt content. These systems contrast with freshwater ecosystems, which have a lower salt content."
    },
    {
        "title": "Space Exploration History",
        "content": "Space exploration is the use of astronomy and space technology to explore outer space. While the exploration of space is carried out mainly by astronomers with telescopes, its physical exploration though is conducted both by unmanned robotic space probes and human spaceflight. Space exploration, like its classical form astronomy, is one of the main sources for space science."
    },
    {
        "title": "Evolutionary Biology",
        "content": "Evolution is change in the heritable characteristics of biological populations over successive generations. These characteristics are the expressions of genes that are passed on from parent to offspring during reproduction. Different characteristics tend to exist within any given population as a result of mutation, genetic recombination and other sources of genetic variation. Evolution occurs when evolutionary processes such as natural selection and genetic drift act on this variation."
    },
    {
        "title": "Nanotechnology Applications",
        "content": "Nanotechnology is the manipulation of matter on an atomic, molecular, and supramolecular scale. The earliest, widespread description of nanotechnology referred to the particular technological goal of precisely manipulating atoms and molecules for fabrication of macroscale products, also now referred to as molecular nanotechnology. Nanotechnology as defined by size is naturally broad, including fields of science as diverse as surface science, organic chemistry, molecular biology, semiconductor physics, and microfabrication."
    },
    {
        "title": "Neuroscience Research",
        "content": "Neuroscience is the scientific study of the nervous system. It is a multidisciplinary science that combines physiology, anatomy, molecular biology, developmental biology, cytology, computer science and mathematical modeling to understand the fundamental and emergent properties of neurons and neural circuits. The understanding of the biological basis of learning, memory, behavior, perception, and consciousness has been described by Eric Kandel as the ultimate challenge of the biological sciences."
    }
]

BUSINESS_DOCS = [
    {
        "title": "Digital Marketing Strategies",
        "content": "Digital marketing is the component of marketing that uses the Internet and online based digital technologies such as desktop computers, mobile phones and other digital media and platforms to promote products and services. Its development during the 1990s and 2000s changed the way brands and businesses use technology for marketing. As digital platforms became increasingly incorporated into marketing plans and everyday life, and as people increasingly use digital devices instead of visiting physical shops, digital marketing campaigns have become prevalent."
    },
    {
        "title": "Supply Chain Management",
        "content": "Supply chain management is the management of the flow of goods and services and includes all processes that transform raw materials into final products. It involves the active streamlining of a business's supply-side activities to maximize customer value and gain a competitive advantage in the marketplace. SCM represents an effort by suppliers to develop and implement supply chains that are as efficient and economical as possible."
    },
    {
        "title": "Financial Planning Basics",
        "content": "Financial planning is the process of taking a comprehensive look at your financial situation and building a specific financial plan to reach your goals. As a result, financial planning often delves into multiple areas of finance, including investing, taxes, savings, retirement, your estate, insurance and more. Financial planning can be done on your own or with the help of a certified financial planner."
    },
    {
        "title": "Entrepreneurship Guide",
        "content": "Entrepreneurship is the creation or extraction of value. With this definition, entrepreneurship is viewed as change, generally entailing risk beyond what is normally encountered in starting a business, which may include other values than simply economic ones. An entrepreneur is an individual who creates and/or invests in one or more businesses, bearing most of the risks and enjoying most of the rewards."
    },
    {
        "title": "Project Management Methodologies",
        "content": "Project management is the process of leading the work of a team to achieve all project goals within the given constraints. This information is usually described in project documentation, created at the beginning of the development process. The primary constraints are scope, time, and budget. The secondary challenge is to optimize the allocation of necessary inputs and apply them to meet pre-defined objectives."
    },
    {
        "title": "Corporate Social Responsibility",
        "content": "Corporate social responsibility is a form of international private business self-regulation which aims to contribute to societal goals of a philanthropic, activist, or charitable nature by engaging in or supporting volunteering or ethically-oriented practices. While once it was possible to describe CSR as an internal organizational policy or a corporate ethic strategy, that time has passed as various international laws have been developed and various organizations have used their authority to push it beyond individual or even industry-wide initiatives."
    },
    {
        "title": "E-commerce Trends",
        "content": "Electronic commerce is the activity of electronically buying or selling of products on online services or over the Internet. E-commerce draws on technologies such as mobile commerce, electronic funds transfer, supply chain management, Internet marketing, online transaction processing, electronic data interchange, inventory management systems, and automated data collection systems. E-commerce is in turn driven by the technological advances of the semiconductor industry."
    },
    {
        "title": "Human Resources Management",
        "content": "Human resource management is the strategic approach to the effective and efficient management of people in a company or organization such that they help their business gain a competitive advantage. It is designed to maximize employee performance in service of an employer's strategic objectives. Human resource management is primarily concerned with the management of people within organizations, focusing on policies and systems."
    },
    {
        "title": "Business Analytics",
        "content": "Business analytics refers to the skills, technologies, and practices for continuous iterative exploration and investigation of past business performance to gain insight and drive business planning. Business analytics focuses on developing new insights and understanding of business performance based on data and statistical methods. In contrast, business intelligence traditionally focuses on using a consistent set of metrics to both measure past performance and guide business planning."
    },
    {
        "title": "Sustainable Business Practices",
        "content": "Sustainable business, or a green business, is an enterprise that has minimal negative impact or potentially a positive effect on the global or local environment, community, society, or economy. Often, sustainable businesses have progressive environmental and human rights policies. In general, business is described as green if it matches the following four criteria: It incorporates principles of sustainability into each of its business decisions, It supplies environmentally friendly products or services that replace demand for nongreen products and/or services, It is greener than traditional competition, It has made an enduring commitment to environmental principles in its business operations."
    }
]

HEALTH_DOCS = [
    {
        "title": "Nutrition and Healthy Eating",
        "content": "Nutrition is the science that interprets the nutrients and other substances in food in relation to maintenance, growth, reproduction, health and disease of an organism. It includes ingestion, absorption, assimilation, biosynthesis, catabolism and excretion. The diet of an organism is what it eats, which is largely determined by the availability and palatability of foods. A healthy diet includes preparation of food and storage methods that preserve nutrients from oxidation, heat or leaching, and that reduces risk of foodborne illnesses."
    },
    {
        "title": "Mental Health Awareness",
        "content": "Mental health includes our emotional, psychological, and social well-being. It affects how we think, feel, and act. It also helps determine how we handle stress, relate to others, and make healthy choices. Mental health is important at every stage of life, from childhood and adolescence through adulthood. Over the course of your life, if you experience mental health problems, your thinking, mood, and behavior could be affected."
    },
    {
        "title": "Exercise and Fitness",
        "content": "Physical fitness is a state of health and well-being and, more specifically, the ability to perform aspects of sports, occupations and daily activities. Physical fitness is generally achieved through proper nutrition, moderate-vigorous physical exercise, and sufficient rest along with a formal recovery plan. Regular exercise is one of the best things you can do for your health. It has many benefits, including improving your overall health and fitness, and reducing your risk for many chronic diseases."
    },
    {
        "title": "Sleep Science",
        "content": "Sleep is a naturally recurring state of mind and body, characterized by altered consciousness, relatively inhibited sensory activity, reduced muscle activity and inhibition of nearly all voluntary muscles during rapid eye movement sleep, and reduced interactions with surroundings. It is distinguished from wakefulness by a decreased ability to react to stimuli, but more reactive than a coma or disorders of consciousness, with sleep displaying different, active brain patterns."
    },
    {
        "title": "Preventive Healthcare",
        "content": "Preventive healthcare consists of measures taken for disease prevention. Disease and disability are affected by environmental factors, genetic predisposition, disease agents, and lifestyle choices and are dynamic processes which begin before individuals realize they are affected. Disease prevention relies on anticipatory actions that can be categorized as primal, primary, secondary, and tertiary prevention."
    },
    {
        "title": "Stress Management Techniques",
        "content": "Stress management consists of a wide spectrum of techniques and psychotherapies aimed at controlling a person's level of stress, especially chronic stress, usually for the purpose of and for the motive of improving everyday functioning. Stress produces numerous physical and mental symptoms which vary according to each individual's situational factors. These can include a decline in physical health, such as headaches, chest pain, fatigue, and sleep problems, as well as depression."
    },
    {
        "title": "Immunology Basics",
        "content": "Immunology is a branch of biology that covers the study of immune systems in all organisms. Immunology charts, measures, and contextualizes the physiological functioning of the immune system in states of both health and diseases; malfunctions of the immune system in immunological disorders; and the physical, chemical, and physiological characteristics of the components of the immune system in vitro, in situ, and in vivo."
    },
    {
        "title": "Chronic Disease Management",
        "content": "Chronic diseases are defined broadly as conditions that last 1 year or more and require ongoing medical attention or limit activities of daily living or both. Chronic diseases such as heart disease, cancer, and diabetes are the leading causes of death and disability in the United States. They are also leading drivers of the nation's healthcare costs. Many chronic diseases are caused by a short list of risk behaviors including tobacco use and exposure to secondhand smoke, poor nutrition, lack of physical activity, and excessive alcohol use."
    },
    {
        "title": "Telemedicine and Digital Health",
        "content": "Telemedicine is the use of telecommunication and information technology to provide clinical health care from a distance. It has been used to overcome distance barriers and to improve access to medical services that would often not be consistently available in distant rural communities. It is also used to save lives in critical care and emergency situations. Telemedicine can be as simple as two health professionals discussing a case over the telephone, or as complex as using satellite technology and videoconferencing equipment to conduct a real-time consultation between medical specialists in two different countries."
    },
    {
        "title": "Public Health Policy",
        "content": "Public health is the science and art of preventing disease, prolonging life and promoting health through the organized efforts and informed choices of society, organizations, public and private communities and individuals. Analyzing the determinants of health of a population and the threats it faces is the basis for public health. The public can be as small as a handful of people or as large as a village or an entire city; in the case of a pandemic it may encompass several continents."
    }
]

EDUCATION_DOCS = [
    {
        "title": "Online Learning Platforms",
        "content": "Online learning is education that takes place over the Internet. It is often referred to as e-learning among other terms. However, online learning is just one type of distance learning - the umbrella term for any learning that takes place across distance and not in a traditional classroom. Online learning can happen synchronously or asynchronously. Synchronous learning is when students learn at the same time, such as in a live online class. Asynchronous learning is when students learn at different times, such as by watching recorded lectures."
    },
    {
        "title": "Educational Technology",
        "content": "Educational technology is the combined use of computer hardware, software, and educational theory and practice to facilitate learning. When referred to with its abbreviation, EdTech, it is often referring to the industry of companies that create educational technology. In addition to practical educational experience, educational technology is based on theoretical knowledge from various disciplines such as communication, education, psychology, sociology, artificial intelligence, and computer science."
    },
    {
        "title": "STEM Education Importance",
        "content": "STEM is a curriculum based on the idea of educating students in four specific disciplines — science, technology, engineering and mathematics — in an interdisciplinary and applied approach. Rather than teach the four disciplines as separate and discrete subjects, STEM integrates them into a cohesive learning paradigm based on real-world applications. STEM education creates critical thinkers, increases science literacy, and enables the next generation of innovators."
    },
    {
        "title": "Early Childhood Development",
        "content": "Early childhood development is the period from prenatal development to age 8. This is a crucial stage where the brain develops rapidly and lays the foundation for future learning, behavior, and health. Quality early childhood education programs can have lasting positive effects on children's development and learning. Research shows that the early years are critical for brain development, and experiences during this time have a lasting impact on a child's future."
    },
    {
        "title": "Special Education Services",
        "content": "Special education is the practice of educating students in a way that accommodates their individual differences, disabilities, and special needs. Ideally, this process involves the individually planned and systematically monitored arrangement of teaching procedures, adapted equipment and materials, and accessible settings. These interventions are designed to help individuals with special needs achieve a higher level of personal self-sufficiency and success in school and in their community."
    },
    {
        "title": "Assessment and Evaluation",
        "content": "Educational assessment is the systematic process of documenting and using empirical data on the knowledge, skill, attitudes, and beliefs to refine programs and improve student learning. Assessment data can be obtained from directly examining student work to assess the achievement of learning outcomes or can be based on data from which one can make inferences about learning. Assessment is often used interchangeably with test, but not limited to tests."
    },
    {
        "title": "Curriculum Development",
        "content": "Curriculum development is the process of designing and creating structures for instruction in schools and other educational settings. The process typically involves identifying learning objectives, developing teaching materials and assessments, and evaluating the effectiveness of the curriculum. Curriculum development can be done by individual teachers, teams of teachers, school districts, or educational organizations. The goal is to create a coherent and effective educational program that meets the needs of students."
    },
    {
        "title": "Student Engagement Strategies",
        "content": "Student engagement refers to the degree of attention, curiosity, interest, optimism, and passion that students show when they are learning or being taught, which extends to the level of motivation they have to learn and progress in their education. Student engagement is a multifaceted concept that includes behavioral, emotional, and cognitive dimensions. Engaged students are more likely to succeed academically and develop positive attitudes toward learning."
    },
    {
        "title": "Inclusive Education",
        "content": "Inclusive education means all children in the same classrooms, in the same schools. It means real learning opportunities for groups who have traditionally been excluded – not only children with disabilities, but speakers of minority languages too. Inclusive systems value the unique contributions students of all backgrounds bring to the classroom and allow diverse groups to grow side by side, to the benefit of all. Inclusive education is about how we develop and design our schools, classrooms, programs and activities so that all students learn and participate together."
    },
    {
        "title": "Lifelong Learning",
        "content": "Lifelong learning is the ongoing, voluntary, and self-motivated pursuit of knowledge for either personal or professional reasons. It is important for an individual's competitiveness and employability, but also enhances social inclusion, active citizenship, and personal development. Lifelong learning can be formal or informal, and takes place throughout an individual's life, from cradle to grave. It recognizes that humans have a natural drive to explore, learn and grow and encourages us to improve our own quality of life and sense of self-worth by paying attention to the ideas and goals that inspire us."
    }
]

def generate_documents():
    """Generate 50 fake documents"""
    documents = []
    doc_id = 1
    
    # Combine all document templates
    all_docs = (
        TECHNOLOGY_DOCS + 
        SCIENCE_DOCS + 
        BUSINESS_DOCS + 
        HEALTH_DOCS + 
        EDUCATION_DOCS
    )
    
    # Generate documents
    for doc_template in all_docs:
        document = {
            "document_id": f"doc-{str(doc_id).zfill(3)}",
            "title": doc_template["title"],
            "content": doc_template["content"],
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "word_count": len(doc_template["content"].split()),
                "char_count": len(doc_template["content"]),
                "topic": get_topic(doc_id)
            }
        }
        documents.append(document)
        doc_id += 1
    
    return documents

def get_topic(doc_id):
    """Determine topic based on document ID"""
    if doc_id <= 10:
        return "technology"
    elif doc_id <= 20:
        return "science"
    elif doc_id <= 30:
        return "business"
    elif doc_id <= 40:
        return "health"
    else:
        return "education"

def save_documents(documents, filename="fake_documents.json"):
    """Save documents to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(documents)} documents to '{filename}'")

def generate_embeddings(documents):
    """Generate 1024-dimensional embeddings using Amazon Titan Text Embeddings V2"""
    print(f"\nGenerating embeddings for {len(documents)} documents...")
    print(f"Model: Amazon Titan Text Embeddings V2")
    print(f"Dimensions: 1024")
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-2')
    embeddings = []
    
    for i, doc in enumerate(documents, 1):
        print(f"  {i}/50: Generating embedding for {doc['document_id']}...")
        
        request_body = {
            "inputText": doc['content'],
            "dimensions": 1024,
            "normalize": True
        }
        
        response = bedrock_runtime.invoke_model(
            modelId='amazon.titan-embed-text-v2:0',
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        embedding = np.array(response_body['embedding'], dtype=np.float32)
        embeddings.append(embedding)
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    embeddings = np.array(embeddings)
    print(f"\n✓ Generated {len(embeddings)} embeddings")
    print(f"  Embedding dimension: {embeddings.shape[1]}")
    
    return embeddings

def save_embeddings(documents, embeddings, output_dir="embeddings"):
    """Save embeddings as binary files"""
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nSaving embeddings to '{output_dir}/' directory...")
    
    for doc, embedding in zip(documents, embeddings):
        doc_id = doc['document_id']
        filename = f"{output_dir}/{doc_id}.bin"
        
        # Save as float32 little-endian binary
        embedding.tofile(filename)
    
    print(f"✓ Saved {len(embeddings)} embedding files")
    print(f"  Format: float32 little-endian binary")
    print(f"  Size per file: {embeddings.shape[1] * 4} bytes ({embeddings.shape[1]} dimensions × 4 bytes)")

def print_summary(documents):
    """Print summary of generated documents"""
    print("\n" + "="*60)
    print("  Document Generation Summary")
    print("="*60)
    print(f"\nTotal documents: {len(documents)}")
    
    # Count by topic
    topics = {}
    for doc in documents:
        topic = doc["metadata"]["topic"]
        topics[topic] = topics.get(topic, 0) + 1
    
    print("\nDocuments by topic:")
    for topic, count in sorted(topics.items()):
        print(f"  {topic.capitalize()}: {count}")
    
    print("\nSample documents:")
    for i, doc in enumerate(documents[:3], 1):
        print(f"\n{i}. {doc['title']}")
        print(f"   ID: {doc['document_id']}")
        print(f"   Topic: {doc['metadata']['topic']}")
        print(f"   Words: {doc['metadata']['word_count']}")
        print(f"   Preview: {doc['content'][:100]}...")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("  Fake Document & Embedding Generator")
    print("="*60)
    
    # Step 1: Generate documents
    print("\n[Step 1/3] Generating 50 fake documents...")
    documents = generate_documents()
    
    # Step 2: Save documents
    print("\n[Step 2/3] Saving documents...")
    save_documents(documents)
    
    # Step 3: Generate and save embeddings
    print("\n[Step 3/3] Generating embeddings with Titan V2...")
    embeddings = generate_embeddings(documents)
    save_embeddings(documents, embeddings)
    
    # Print summary
    print_summary(documents)
    
    print("\n" + "="*60)
    print("  Generation Complete!")
    print("="*60)
    print("\nGenerated files:")
    print("  1. fake_documents.json - Document content and metadata")
    print("  2. embeddings/*.bin - Binary embedding files (50 files, 1024 dims)")
    print("\nNext steps:")
    print("  1. Insert document metadata into Aurora database")
    print("  2. Create test users and permissions")
    print("  3. Upload embeddings to S3 Vectors")
    print("  4. Create Bedrock Knowledge Base")

if __name__ == "__main__":
    main()

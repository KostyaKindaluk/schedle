import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Alert, Card, Table, Spinner, Row, Col, Badge } from 'react-bootstrap';
import { useAuthStore } from "@src/scripts/state";
import { getSchedulingDetail } from "@src/scripts/api";

function SchedulingDetailPage() {
  const { id } = useParams();
  const { token } = useAuthStore();
  
  const [scheduling, setScheduling] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      try {
        const data = await getSchedulingDetail(token, id);
        setScheduling(data);
        setError('');
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id, token]);

  if (loading) {
    return (
      <Container className="mt-4 text-center">
        <Spinner animation="border" />
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  if (!scheduling || !scheduling.best_schedules || scheduling.best_schedules.length === 0) {
    return (
      <Container className="mt-4">
        <Alert variant="warning">No schedule data available</Alert>
      </Container>
    );
  }

  const schedule = scheduling.best_schedules[0];
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  
  return (
    <Container className="mt-4">
      <h2 className="mb-4">Details of "{scheduling.name}" scheduling</h2>

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Input Parameters</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={4}>
              <p><strong>Duration:</strong> {scheduling.duration_weeks} weeks</p>
              <p><strong>Max daily slots:</strong> {scheduling.max_daily_slots}</p>
              <p><strong>Desired days per week:</strong> {scheduling.desired_days_count}</p>
            </Col>
            <Col md={8}>
              {scheduling.final_fitness !== null && (
                <p><strong>Final fitness score:</strong> {scheduling.final_fitness.toFixed(2)}</p>
              )}
              <p><strong>Status:</strong> <Badge bg={scheduling.status === 'completed' ? 'success' : 'warning'}>{scheduling.status}</Badge></p>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Subjects</h5>
        </Card.Header>
        <Card.Body>
          <div className="d-flex flex-wrap gap-2">
            {scheduling.subjects && scheduling.subjects.map((subj, idx) => (
              <Badge key={idx} bg="secondary" className="p-2">{subj.name}</Badge>
            ))}
          </div>
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Groups and Their Subjects</h5>
        </Card.Header>
        <Card.Body>
          {scheduling.groups && scheduling.groups.map((group, idx) => (
            <div key={idx} className="mb-3">
              <h6>{group.name}</h6>
              <Table size="sm" bordered>
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Lectures</th>
                    <th>Practices</th>
                  </tr>
                </thead>
                <tbody>
                  {group.subjects && group.subjects.map((subj, sIdx) => (
                    <tr key={sIdx}>
                      <td>{subj.subject}</td>
                      <td>{subj.lectures}</td>
                      <td>{subj.practices}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          ))}
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Teachers</h5>
        </Card.Header>
        <Card.Body>
          {scheduling.teachers && scheduling.teachers.map((teacher, idx) => (
            <div key={idx} className="mb-3">
              <h6>{teacher.name}</h6>
              <Table size="sm" bordered>
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Can Lecture</th>
                    <th>Can Practice</th>
                  </tr>
                </thead>
                <tbody>
                  {teacher.subjects && teacher.subjects.map((subj, sIdx) => (
                    <tr key={sIdx}>
                      <td>{subj.subject}</td>
                      <td>{subj.is_lecturer ? '✓' : '—'}</td>
                      <td>{subj.is_practitioner ? '✓' : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          ))}
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Classrooms</h5>
        </Card.Header>
        <Card.Body>
          <div className="d-flex flex-wrap gap-2">
            {scheduling.classrooms && scheduling.classrooms.map((room, idx) => (
              <Badge key={idx} bg="info" className="p-2">{room.name}</Badge>
            ))}
          </div>
        </Card.Body>
      </Card>

      <h3 className="mt-4 mb-3">Generated Schedule</h3>
      {schedule.groups && schedule.groups.map((group) => (
        <Card key={group} className="mb-4">
          <Card.Body>
            <Card.Title>{group}</Card.Title>
            <Table bordered size="sm">
              <thead>
                <tr>
                  <th>Slot</th>
                  {days.map((day) => (
                    <th key={day}>{day}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Array.from({ length: scheduling.max_daily_slots }, (_, slotIdx) => (
                  <tr key={slotIdx}>
                    <td><strong>{slotIdx + 1}</strong></td>
                    {days.map((_, dayIdx) => {
                      const slot = schedule.timetables?.[group]?.[dayIdx]?.[slotIdx];
                      if (!slot || slot.is_empty) {
                        return <td key={dayIdx} style={{ backgroundColor: '#e9ecef' }}></td>;
                      }
                      
                      const bgColor = slot.lesson_type === 'lecture' 
                        ? '#fff2c7ff'
                        : '#c0e1ffff';
                      
                      return (
                        <td key={dayIdx} style={{ backgroundColor: bgColor }}>
                          <div><strong>{slot.subject}</strong></div>
                          <div><small>{slot.lesson_type === 'lecture' ? 'Lecture' : 'Practice'}</small></div>
                          <div><small>{slot.teacher}</small></div>
                          <div><small>Room: {slot.classroom}</small></div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card.Body>
        </Card>
      ))}
    </Container>
  );
}

export { SchedulingDetailPage };